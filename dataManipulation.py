# Import Modules
try:
    import os, sys, shutil
    from zipfile import ZipFile
    import glob
    import pandas as pd
    import numpy as np
    # Import local modules
    sys.path.append(os.path.abspath('shared'))
    import directory
except ImportError:
    print(ImportError)
    sys.exit()

# Directory management
main_dir = os.path.abspath('.').split('/')[-1]
input_dir = f"../{main_dir}_input/"
output_dir = f"../{main_dir}_output/"
raw_dir = f"{input_dir}raw/"
rawData_dir = f"{raw_dir}request/"
rawUnzip_dir = f"{raw_dir}unzip/"


# Find each instance of data. So that you could run a big batch job.
rawData_dirs = glob.glob(f"{rawData_dir}*")

# Copied from geeksforgeeks.org
def getAllFilePaths(directory):
    # initializing empty file paths list
    file_paths = []
    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


for rawRequest_dir in rawData_dirs:
    directory.make_dir(rawUnzip_dir)
    # Verify that zip files are closed
    try: zip.close()
    except: pass
    zip = ZipFile(rawRequest_dir+'/abun_enviro_data.zip','r')
    zip.extractall(rawUnzip_dir)
    # Clean up zip files
    zip.close()

    # Parse environmental data
    env_par = pd.read_csv(f'{rawUnzip_dir}environmental_parameters.csv', sep = '\t')
    gene_ab = pd.read_csv(f'{rawUnzip_dir}abundance_matrix.csv', sep = '\t', skiprows = [1])

    gene_ab.insert(0, 'ID', range(1, gene_ab.shape[0]+1)) # assign ID to each row


    taxonomy = gene_ab['Unnamed: 1'].str.split('; ',expand=True)
    #gene_ab = pd.concat([taxonomy, gene_ab], axis=1)
    #gene_ab = gene_ab.dropna(axis=0, subset=[1])  
    m = taxonomy[1] != 'Bacteria'
    gene_ab_euk, gene_ab_prok = taxonomy[m], taxonomy[~m] # needed to split data to prokaryotes and non-prokaryotes due to different taxonomic levels

    gene_ab_prok = gene_ab_prok[gene_ab_prok.columns[0:8]]
    gene_ab_prok.columns = ['Biota', 'Superkingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genera', 'Species']
    gene_ab_euk = gene_ab_euk.dropna(axis=0, subset=[0])
    gene_ab_euk.columns = ['Biota', 'Superkingdom', 'Kingdom', 'Superphylum', 'Phylum', 'Subphylum', 'Class', 'Subclass', 'Infraclass',
        'Cohort', 'Order', 'Suborder', 'Infraorder', 'Superfamily', 'Family', 'Subfamily', 'Tribe', 'Genus']

    gene_ab = pd.concat([gene_ab, pd.concat([gene_ab_prok, gene_ab_euk])], axis=1)
    # calculating sum of abundance for each taxonomic level
    gene_ab_melt = gene_ab.melt(id_vars = ['ID', 'Biota', 'Superkingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genera', 'Species', 'Kingdom', 'Superphylum', 'Subphylum', 'Subclass', 'Infraclass', 'Cohort', 'Suborder', 'Infraorder', 'Superfamily', 'Subfamily', 'Tribe', 'Genus'])
    dummy = pd.get_dummies(gene_ab_melt, columns = ['Biota', 'Superkingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genera', 'Species', 'Kingdom', 'Superphylum', 'Subphylum', 'Subclass', 'Infraclass', 'Cohort', 'Suborder', 'Infraorder', 'Superfamily', 'Subfamily', 'Tribe', 'Genus'], dtype = int)
    for col in dummy.columns.to_list():
        if col != ['value'] and dummy[col].dtype == 'int':
            dummy[col] = np.where(dummy[col] == 1, dummy['value'], dummy[col])
    gene_ab_final = dummy.groupby('variable').sum().reset_index().rename({'variable' : 'rownames'}, axis=1).drop('value', axis=1)

    # merged environmental parameters and gene abundance into one file
    alldata = pd.merge(left=env_par, right=gene_ab_final, how='left', left_on='OGA_ID.1', right_on='rownames')

    # Save merged data to pickle
    req = rawRequest_dir.split('/')[-1]+"/"
    directory.make_dir(f'{output_dir}{req}')
    alldata.to_pickle(f'{output_dir}{req}dataProc.p')
    # Zip input folder
    try: zip.close()
    except: pass
    file_paths = getAllFilePaths(rawRequest_dir)
    with ZipFile(f'{output_dir}{req}{req[:-1]}.zip','w') as zip:
        for file in file_paths:
            zip.write(file)
        zip.close()
    shutil.rmtree(rawUnzip_dir)
    shutil.rmtree(rawRequest_dir)

    # TO DO:
    # Clean up.  delete unzip folder.
