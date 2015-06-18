from pandas import read_csv
from liverx import wd

# ---- Create ID maps
# Id map between Ensemble and UniProt
id_map = read_csv(wd + '/files/genemania_mouse_identifier_mappings.txt', sep='\t')
id_map = id_map[id_map['Source'] == 'Uniprot ID']
id_map = id_map[[x.endswith('_MOUSE') for x in id_map['Name']]]
id_map = id_map.drop_duplicates(subset=['Preferred_Name'])
id_map = id_map.set_index('Preferred_Name')['Name']
id_map.to_csv('%s/files/GeneMania_Ensemble_UniProt.tab' % wd, sep='\t')
id_map = id_map.to_dict()
print '[INFO] ENS to Uniprot map: ', len(id_map)

# Id map between Ensemble and Entrez
id_map_entrez = read_csv(wd + '/files/genemania_mouse_identifier_mappings.txt', sep='\t')
id_map_entrez = id_map_entrez[id_map_entrez['Source'] == 'Entrez Gene ID']
id_map_entrez = id_map_entrez.drop_duplicates(subset=['Preferred_Name'])
id_map_entrez = id_map_entrez.set_index('Preferred_Name')['Name']
id_map_entrez.to_csv('%s/files/GeneMania_Ensemble_Entrez.tab' % wd, sep='\t')
print '[INFO] ENS to EntrezID map: ', len(id_map_entrez)

# Id map between Ensemble and Gene Name
id_map_gene_name = read_csv(wd + '/files/genemania_mouse_identifier_mappings.txt', sep='\t')
id_map_gene_name = id_map_gene_name[id_map_gene_name['Source'] == 'Gene Name']
id_map_gene_name = id_map_gene_name.drop_duplicates(subset=['Preferred_Name'])
id_map_gene_name = id_map_gene_name.set_index('Preferred_Name')['Name']
id_map_gene_name.to_csv('%s/files/GeneMania_Ensemble_GeneName.tab' % wd, sep='\t')
print '[INFO] ENS to Gene Name map: ', len(id_map_gene_name)

# ---- Import GeneMania mouse network
# Import network
network = read_csv(wd + '/files/COMBINED.DEFAULT_NETWORKS.BP_COMBINING.txt', sep='\t')
print '[INFO] GeneMania mouse PIP network', network.shape

# Remove interactions with weight lower than X threshold
for thres in [10**-4, 10**-3]:
    print '[INFO] Weight threshold: %.1e' % thres

    subnetwork = network[network['Weight'] >= thres]
    print '[INFO] Remove interactions with weight below %f: ' % thres, subnetwork.shape

    # Remove self interactions
    subnetwork = subnetwork[[a != b for a, b in zip(*(subnetwork['Gene_A'], subnetwork['Gene_B']))]]
    print '[INFO] Remove self interactions: ', subnetwork.shape

    # Remove interactions without mapping ID
    subnetwork = subnetwork[[a in id_map and b in id_map for a, b in zip(*(subnetwork['Gene_A'], subnetwork['Gene_B']))]]
    print '[INFO] Remove interactions without any measured node: ', subnetwork.shape

    # Convert ENS to Uniprot
    subnetwork['Gene_A'] = [id_map[i] for i in subnetwork['Gene_A']]
    subnetwork['Gene_B'] = [id_map[i] for i in subnetwork['Gene_B']]

    # Export to file
    subnetwork[['Gene_A', 'Gene_B']].to_csv('%s/files/genemania_mouse_network_filtered_%.0e.txt' % (wd, thres), sep='\t', index=False)