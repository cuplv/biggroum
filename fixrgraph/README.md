# Janus scheduler

The scheduler performs two tasks:

1. Create a list of jobs
python create_jobs.py  -i <path-to-index.json> -g <path-to-graphs> -j <out-directory-jobs> -o <out-dir-iso> -s <job-size> 

-p <path_to_run_iso.py> -i <path-to-iso-bin>
-t <to in seconds> 
-s <scratch-path> 


NOTE - the following paths MUST be reachable from the Janus nodes
- <path-to-graphs>
- <out-directory-jobs>
- <out-dir-iso>
- <directory-jobs>
- <path_to_run_iso>
- <path-to-iso-bin>
- <scratch-path>


E.g. python create_jobs.py -i index.json -g /home/sergio/works/projects/muse/test_app_graphs/graphs -b /home/sergio/works/projects/muse/repos/FixrGraphIso/build/src/fixrgraphiso/fixrgraphiso -p /home/sergio/works/projects/muse/repos/FixrGraphIndexer/scheduler/run_iso.py -l /tmp -j /home/sergio/works/projects/muse/test_app_graphs/scheduler -o /home/sergio/works/projects/muse/test_app_graphs/isomorphism2 -f -t 10 


# LOG
python process_logs.py -s /home/sergio/works/projects/muse/data/compressed_jobs/test_indexer.json -j /home/sergio/works/projects/muse/data/compressed_jobs -n /lustre/janus_scratch/semo2007/jobs -o test_log.txt

process_logs.py -s /home/sergio/works/projects/muse/data/compressed_jobs/test_indexer.json -j /home/sergio/works/projects/muse/data/compressed_jobs -n /lustre/janus_scratch/semo2007/jobs -o test_log.txt -g /lustre/janus_scratch/semo2007/new_graphs

python gen_html.py  -db /home/sergio/works/projects/muse/data/log_db.db -o /tmp/iso_index -g /home/sergio/works/projects/muse/data/new_graphs -p /home/sergio/works/projects/muse/data/new_provenance -i /home/sergio/works/projects/muse/data/new_isomorphisms


# Generate html pages for isomorphism
`gen_html.py`
