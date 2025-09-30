
import re
import pandas as pd

def calculate_snp_stats(df, rs_id, snp_stats):

    snp_df = df.rename(columns={'rsid': 'pid'})
    snp_df = snp_df.set_index('pid').T

    valid_pattern = re.compile(r'^[AGCT]{2}$') 
    snp_series = snp_df[rs_id] 

    snp_df = snp_df[[rs_id]].copy() 
    snp_df.rename(columns={rs_id: 'snp'}, inplace=True)
    unique_genos = snp_series.unique()

    missing_mask = ~snp_series.str.match(valid_pattern)
    missing_count = missing_mask.sum()

    valid_genotypes = snp_series[~missing_mask].unique()

    print(f"\t--{missing_count} participants with missing/invalid reads for {rs_id}")
    print(f"\t--{len(valid_genotypes)} unique genotypes found for {rs_id}")

    unique_genos = [x for x in unique_genos if valid_pattern.match(x)]

    filtered_df = snp_df[snp_df['snp'].apply(lambda x: bool(valid_pattern.match(x)))]

    sample_size = len(filtered_df)
    allele_pool = sample_size * 2

    alleles = [x for x in ''.join(unique_genos)]
    alleles = list(set(alleles))

    if len(alleles) == 1:
        allele1 = alleles[0]
        allele2 = '/'
        allele_1_freq = 1
        allele_1_freq = str(allele_1_freq)
        allele1 = allele1 + " (" + allele_1_freq + ")"
        
        #now set the hmz_maj to 1 and the rest to 0
        hmz_maj = 1
        htz = 0
        hmz_min = 0
        
        maf = 0
        
        snp_stats_row = pd.DataFrame({'rsid': [rs_id], 'allele1': [allele1], 'allele2': [allele2], 'sample_size': [sample_size], 'hmz_maj': [hmz_maj], 'htz': [htz], 'hmz_min': [hmz_min], 'maf': [maf]})
        
        #concatenate the row to the snp_stats DataFrame
        snp_stats = pd.concat([snp_stats, snp_stats_row])
        
    elif len(alleles) == 2:
        allele1 = alleles[0]
        allele2 = alleles[1]
        allele1_count = filtered_df['snp'].apply(lambda x: x.count(allele1)).sum()
        allele2_count = filtered_df['snp'].apply(lambda x: x.count(allele2)).sum()
        total_count = allele1_count + allele2_count

        if total_count != allele_pool:
            print(f"\t--Error: total count {total_count} does not match allele pool {allele_pool}")
        else:
            print("\t--all alleles accounted for")

        allele_1_freq = allele1_count / allele_pool
        allele_2_freq = allele2_count / allele_pool
        allele_1_freq = round(allele_1_freq, 3)
        allele_2_freq = round(allele_2_freq, 3)
        allele_1_freq = str(allele_1_freq)
        allele_2_freq = str(allele_2_freq)
        allele1_str = allele1 + " (" + allele_1_freq + ")"
        allele2_str = allele2 + " (" + allele_2_freq + ")"
        
        #determine which allele is major and which is minor
        if allele_1_freq > allele_2_freq:
            major_allele = allele1
            minor_allele = allele2
        else:
            major_allele = allele2
            minor_allele = allele1
            
        #print the major and minor alleles
        print(f"\t--Major allele: {major_allele}")
        print(f"\t--Minor allele: {minor_allele}")
        
        #now calculate the freq of each genotype, first defining them
        hmz_maj = major_allele + major_allele
        htz_1 = major_allele + minor_allele
        htz_2 = minor_allele + major_allele
        hmz_min = minor_allele + minor_allele
        
        #count the number of each genotype in the filtered_df rsid column
        hmz_maj_count = filtered_df['snp'].apply(lambda x: x.count(hmz_maj)).sum()
        htz_1_count = filtered_df['snp'].apply(lambda x: x.count(htz_1)).sum()
        htz_2_count = filtered_df['snp'].apply(lambda x: x.count(htz_2)).sum()
        htz_count = htz_1_count + htz_2_count
        hmz_min_count = filtered_df['snp'].apply(lambda x: x.count(hmz_min)).sum()
        
        #if hmz_min_count is 0, set hmz_min_freq to 0
        if hmz_min_count == 0:
            hmz_min_freq = 0
        else:
            hmz_min_freq = hmz_min_count / sample_size
            
        #now calculate the freq of each genotype
        hmz_maj_freq = hmz_maj_count / sample_size
        htz_freq = htz_count / sample_size

        #round each to 3 decimal places
        hmz_maj_freq = round(hmz_maj_freq, 3)
        htz_freq = round(htz_freq, 3)
        hmz_min_freq = round(hmz_min_freq, 3)
        
        #now convert each to string
        hmz_maj_freq = str(hmz_maj_freq)
        htz_freq = str(htz_freq)
        hmz_min_freq = str(hmz_min_freq)
        
        #determine if htz_1 or htz_2 is showing up in the filtered_df rsid column
        if htz_1_count > htz_2_count:
            htz = htz_1
        else:
            htz = htz_2
        
        #now concatenate the hz_maj, hzt and hz_min strings with their frequencies
        hmz_maj_freq_str = hmz_maj + " (" + hmz_maj_freq + ")"
        htz_freq_str = htz + " (" + htz_freq + ")"
        hmz_min_freq_str = hmz_min + " (" + hmz_min_freq + ")"
        
        #finally assign a maf value, which is simply the freq of the minor allele
        maf = min(allele_1_freq, allele_2_freq)

        snp_stats_row = pd.DataFrame({'rsid': [rs_id], 'allele1': [allele1_str], 'allele2': [allele2_str], 'sample_size': [sample_size], 'hmz_maj': [hmz_maj_freq_str], 'htz': [htz_freq_str], 'hmz_min': [hmz_min_freq_str], 'maf': [maf]})
        
        #concatenate the row to the snp_stats DataFrame
        snp_stats = pd.concat([snp_stats, snp_stats_row])

    elif len(alleles) > 2:

        return None

    return snp_stats

def split_snp_stats(combined_query_df):

    status_dict = {"adults": "", "children": "", "both": ""}

    #filter combined_query df for rsid and all columns starting with "s" or "p"
    adult_query_df = combined_query_df.filter(regex='rsid|s|p')
    child_query_df = combined_query_df.filter(regex='rsid|a|b|c')

    #assign rsids as a list
    rsids = combined_query_df['rsid'].tolist()

    #Create a DataFrame to store info on alleles
    snp_stats_adult = pd.DataFrame(columns=['rsid', 'allele1', 'allele2', 'sample_size', 'hmz_maj', 'htz','hmz_min', 'maf'])

    #now loop over each rsid in the combined_query_df rsid column and apply the calculate_snp_stats function

    for rs_id in rsids:
        print(f"\nCalculating stats for {rs_id}")
        snp_stats_adult = calculate_snp_stats(adult_query_df, rs_id, snp_stats_adult)
        
    #convert maf to numeric
    snp_stats_adult['maf'] = pd.to_numeric(snp_stats_adult['maf'])
        
    #repeat for children
    #Create a DataFrame to store info on alleles
    snp_stats_child = pd.DataFrame(columns=['rsid', 'allele1', 'allele2', 'sample_size', 'hmz_maj', 'htz','hmz_min', 'maf'])

    #now loop over each rsid in the combined_query_df rsid column and apply the calculate_snp_stats function
    for rs_id in rsids:
        print(f"\nCalculating stats for {rs_id}")
        snp_stats_child = calculate_snp_stats(child_query_df, rs_id, snp_stats_child)
        
    #convert maf to numeric
    snp_stats_child['maf'] = pd.to_numeric(snp_stats_child['maf'])

    #add a criteria_warning to both dfs
    snp_stats_adult['criteria_warning'] = ""
    snp_stats_child['criteria_warning'] = ""

    #Loop over each row in snp_stats_adult
    for index, row in snp_stats_adult.iterrows():

        if row['maf'] < 0.05:
            if row['allele2'] == "/":
                snp_stats_adult.at[index, 'criteria_warning'] = "mono-allelic"
            else:
                snp_stats_adult.at[index, 'criteria_warning'] = "low_maf"

    #Loop over each row in snp_stats_child
    for index, row in snp_stats_child.iterrows():
        #If any of the values in maf are less than 0.05, then set the status_dict to "low_maf"
        if row['maf'] < 0.05:
            if row['allele2'] == "/":
                snp_stats_child.at[index, 'criteria_warning'] = "mono-allelic"
            else:
                snp_stats_child.at[index, 'criteria_warning'] = "low_maf"

    #if any of the values in maf are less than 0.05, then set the status_dict to "low_maf"
    if snp_stats_adult['maf'].min() < 0.05:
        status_dict['adults'] = "failed"
        
    if snp_stats_child['maf'].min() < 0.05:
        status_dict['children'] = "failed"

    return snp_stats_adult, snp_stats_child, status_dict


def genetic_query(query_df, snp_list):

    if query_df is not None and not query_df.empty:

        exact_mask = query_df['manifest_name'].isin(snp_list)
    
        possible_mask = query_df['possible_rsids'].apply(
            lambda x: any(snp in str(x).split(';') for snp in snp_list)
        )
    
        probable_mask = possible_mask & ~exact_mask
        
        #add match_type column
        query_df['match_type'] = 'exact'
        query_df.loc[probable_mask, 'match_type'] = 'probable'
        
        #replace manifest_name with the actual SNP from snp_list for probable matches
        def pick_matching_snp(possible_rsids):
            for snp in str(possible_rsids).split(';'):
                if snp in snp_list:
                    return snp
            return None  

        query_df.loc[probable_mask, 'manifest_name'] = query_df.loc[probable_mask, 'possible_rsids'].apply(pick_matching_snp)

        #drop unnecessary columns for counting
        snp_stats_df = query_df.drop(columns=['possible_rsids', 'nucleotides', 'prefix', 'match_type'])
        snp_stats_df = snp_stats_df.rename(columns={'manifest_name': 'rsid'})

        snp_stats_adult, snp_stats_child, status_dict = split_snp_stats(snp_stats_df)

        ## ****** THIS IS MAIN COUNT BASED part for databasewebb app

        #for counts in queries in the database app, we can simply format the output here after filtering for valid reads!

        counts_df = snp_stats_df.rename(columns={'rsid': 'pid'})
        counts_df = counts_df.set_index('pid').T

        valid_pattern = re.compile(r'^[AGCT]{2}$') 
        valid_mask = counts_df.applymap(lambda x: bool(valid_pattern.match(str(x))))

        counts_adults = counts_df[counts_df.index.str[0].isin(['p', 's'])]
        counts_children = counts_df[counts_df.index.str[0].isin(['a', 'b', 'c'])]

        counts_adults = counts_adults[valid_mask.all(axis=1)]
        counts_children = counts_children[valid_mask.all(axis=1)]


    #return sample size of valid reads in adults and in children
    return counts_adults, counts_children