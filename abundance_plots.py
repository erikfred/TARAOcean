"""
Make plots from environmental and abundance data. Who knows what these will be
at this point...
"""

# imports
try:
    import os, sys
    import glob
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import argparse
    import cartopy
    import cartopy.crs as ccrs
    import pickle
    # Import local modules
    sys.path.append(os.path.abspath('shared'))
    import directory, TARA
except ImportError:
    print(ImportError)
    sys.exit()

# parser to request filename and rank from user
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', default='dataProc.p', type=str,
    help="Name of environmental and adundance data file (.p)")
parser.add_argument('-r', '--rank', default='Superkingdom', type=str,
    help="Taxonomic rank of interest")
args = parser.parse_args()
filename = args.filename
if not filename[-2:] == '.p':
    filename = filename + '.p' # adds extension if needed
tax_rank = args.rank.capitalize() # to ensure string match with column headers

# directory management
main_dir = os.path.abspath('.').split('/')[-1]
output_dir = f"../{main_dir}_output/"

# find all directories from dataManipulation.py
pickle_dirs = glob.glob(f"{output_dir}*")

# loop through each directory and make requested plots
for fldr in pickle_dirs:
    pik_dir = fldr + '/'

    # additional directory management
    fig_dir = pik_dir + "figures/"
    directory.make_dir(fig_dir)
    rank_dir = fig_dir + tax_rank + "/"
    directory.make_dir(rank_dir)

    # load  pickle file, if it exists and is accessible
    try:
        my_pick = open(pik_dir + filename, 'rb')
        df_all = pickle.load(my_pick)
        my_pick.close()
    except FileNotFoundError:
        print(f"File: {filename} does not exist")
        sys.exit()
    except IOError:
        print(f"File: {filename} is not accessible")
        sys.exit()

    # isolate lat/lon of all data points
    df_latlon=df_all[['latitude','longitude']]

    # pull information by taxonomic level (from argument parser)
    abundance = df_all['Biota_Biota']
    member_list = [col for col in df_all.columns if tax_rank in col]
    member_str = [i.strip(tax_rank + '_') for i in member_list] # for labels later
    df_member = df_all[member_list]

    # pull specific environmental variables (written to make easily interchangeable)
    O2_list = [col for col in df_all.columns if col.startswith('O2')]
    oxy = df_all[O2_list]
    N_list = [col for col in df_all.columns if col.startswith('NO3_NO2')]
    nit = df_all[N_list]

    # get depth bins
    depth = df_all['depth']

    # PLOTTING
    fs = 14 # primary fontsize
    ms = 4 # primary markersize

    # Figure 1
    # simple map of where we have data
    fig1 = plt.figure(figsize=(10,7))
    ax1 = fig1.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude = -20))
    ax1.add_feature(cartopy.feature.LAND, color='burlywood')
    ax1.add_feature(cartopy.feature.OCEAN, color='slateblue')
    ax1.add_feature(cartopy.feature.COASTLINE, edgecolor='white')
    ax1.plot(df_latlon['longitude'], df_latlon['latitude'], linestyle='None',
        marker='o', ms=ms, mfc='gold', mec='gold',
        transform=ccrs.PlateCarree())
    ax1.set_global()

    ax1.set_title('Sample Location Map', weight='bold', fontsize=fs+2)
    fig1.savefig(fig_dir + 'sample_map.png')
    plt.close(fig1)

    # Figures 2 and 3
    # simlar map plot, scaled by abundance
    # produces one map with all the members (usually too many to make sense of)
    # as well as separate maps for each
    fig2 = plt.figure(figsize=(10,7))
    ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude = 0))
    ax2.stock_img()

    cmap = cm.get_cmap('gist_ncar') # essentially a perceptual map b/c purely for distinguishing
    count = 0
    ncol = np.ceil(len(member_str) / 5).astype(int) # if many data columns, need to format legend differently
    amax = df_member.max().max() # part of scaling scheme for scatterplot

    for col in df_member:
        if sum(df_member[col]) == 0:
            continue
        # scheme for scaling points
        norm_col = df_member[col] / amax
        sclf = -1 * np.log10(norm_col[norm_col>0].values).astype(int) + 1

        mc = [list(cmap(count / len(member_str)))] # unique color for each member
        lbl = member_str[count]

        # combined plot (kind of a lot)
        ax2.scatter(df_latlon['longitude'], df_latlon['latitude'], s=500/sclf,
            c=mc, marker='o', alpha=0.25, label=lbl, transform=ccrs.PlateCarree())

        # make separate abundance maps for each member (easier to digest)
        fig3 = plt.figure(figsize=(10,7))
        ax3 = fig3.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude = 0))
        ax3.stock_img()
        ax3.scatter(df_latlon['longitude'], df_latlon['latitude'], s=500/sclf,
            c=mc, marker='o', alpha=0.25, label=lbl, transform=ccrs.PlateCarree())
        ax3.set_title(tax_rank + ' ' + lbl + ' Global Abundance', weight='bold', fontsize=fs+2)
        fig3.savefig(rank_dir + tax_rank + '_' + lbl + '_abundance_map.png')
        plt.close(fig3)

        count += 1

        lh = ax2.legend(loc=8, fontsize=fs/2, ncol=ncol)
        ax2.set_title(tax_rank + ' Global Abundance', weight='bold', fontsize=fs+2)

        fig2.savefig(rank_dir + tax_rank + '_abundance_map.png')
        plt.close(fig2)

    # Figures 4-
    # some scatter plots of total abundance against environmental parameters

    # pare down to only samples at mesopelagic depth
    mes_oxy = oxy[depth=='MES']
    mes_nit = nit[depth=='MES']
    mes_abd = abundance[depth=='MES']

    # do we see low O2 with high abundance?
    fig4 = plt.figure(figsize=(10,10))
    ax4 = fig4.add_subplot(1, 2, 1)
    ax4.semilogy(mes_oxy, mes_abd, linestyle='None', marker='o', ms=ms*2,
        mfc='tomato', mec='tomato')
    ax4.set_xlabel(O2_list[0], fontsize=fs)
    ax4.set_ylabel('Abundance', fontsize=fs)
    #ax4.set_title('Total Abundance in Mesopelagic Zone', weight='bold', fontsize=fs+2)

    # do we see high N with high abundance?
    ax5 = fig4.add_subplot(1, 2, 2)
    ax5.semilogy(mes_nit, mes_abd, linestyle='None', marker='o', ms=ms*2,
        mfc='cornflowerblue', mec='cornflowerblue')
    ax5.set_xlabel(N_list[0], fontsize=fs)
    plt.figtext(0.5, 0.9, 'Total Abundance in Mesopelagic Zone', ha='center', 
        va='center', weight='bold', fontsize=fs+2)

    fig4.savefig(fig_dir + 'abundanceVenv.png')
    plt.close(fig4)
