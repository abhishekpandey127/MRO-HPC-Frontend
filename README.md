# MRO HPC with UI

This is an implementation of the MROptimum SNR calculation that is capable of running on NYU HPC. 

## Pre-requisites
There are some pre-requisites before a user can run this code:
- Obtain an NYU HPC Account
- Setup a Singularity overlay with miniconda (python). More info can be found [here](https://sites.google.com/nyu.edu/nyu-hpc/hpc-systems/greene/software/singularity-with-miniconda).
- Once you've setup the singularity overlay, launch the environment and install MROptimum on /ext3/env.sh
  - Install [MROptimum](https://github.com/cloudmrhub-com/mroptimum) on /ext3/env.sh
  - If you plan on bringing your signal, noise and job files from an external storage platform install and [config rclone for your specific storage platform](https://rclone.org/install/).
- Setup a directory that contains your signal and noise files (in my case it is cloudmrhubdata) 
- Setup a directory that contains your job json (in my case it is mroptimum-jobs) 
- Setup a directory that will be where the mroptimum package will release the outputs

## Preparing the SBatch script
HPC systems use SBatch in order to allocate resources and run commands. Create your own SBatch script along the following lines, replacing commands as per needs/requirements
```bash
#!/bin/bash
#SBATCH --nodes=1                        # requests 1 compute servers
#SBATCH --ntasks-per-node=1              # runs 1 tasks on each server
#SBATCH --cpus-per-task=2                # uses 1 compute core per task
#SBATCH --time=1:00:00                   # Computation time 1hr
#SBATCH --mem=10GB                       # Memory requested 10GB
#SBATCH --job-name=sbatch-mroptimum
#SBATCH --mail-type=END
#SBATCH --mail-user=youremail@domain.com
#SBATCH --output=/scratch/<netID>/your/preferred/path/demo_%j.out
#SBATCH --error=/scratch/<netID>/your/preferred/path/demo_%j.err
#SBATCH --exclusive
#SBATCH --requeue

module purge
module load python/intel/3.8.6

singularity exec --overlay /scratch/<netID>/your/preferred/path/overlay_file.ext3:rw /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif /bin/bash -c "
source /ext3/env.sh
rclone copy remote:cloudmrhubdata /scratch/<netID>/your/preferred/path/cloudmrhubdata/
rclone copy remote:mroptimum-jobs /scratch/<netID>/your/preferred/path/mroptimum-jobs/
python -m mroptimum.snr -j /scratch/<netID>/your/preferred/path/mroptimum-jobs/jobfile.json -o /scratch/<netID>/your/preferred/path/mroptimum-results/ --parallel
rclone copy /scratch/<netID>/your/preferred/path/mroptimum-results remote:mroptimum-results
"
```
PLEASE NOTE: This SBatch script (mro.sbatch) assumes that the prerequisites are met and that you are using an S3 bucket to copy signal, noise and job data over from. If you are using a different storage bucket, or are going to be using scp to transfer files into HPC, these lines may be removed from your iteration of the SBatch script.


## Running the SBatch using the UI
The MROptimum calculations can also be done using this UI. It allows users to bring in their files from S3 buckets and perform calculations. Users can either upload the files manually on AWS Console, or use the UI to upload it by providing their aws_access_key_id and aws_secret_access_key.
```bash
git clone https://github.com/abhishekpandey127/MRO-HPC-Frontend
cd MRO-HPC-Frontend
pip install -r requirements.txt
python app.py
```
The development server will launch at [port 5001](http://127.0.0.1:5001). If port 5001 is unavailable for you, please change the port being requested on your local device.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
