# Conda Setup on DGX On-Prem / HPC

Follow these steps to set up **Conda** on the DGX On-Prem or HPC system.

---

## 1. Initialize Conda in `.bashrc`

Add the following block to your `~/.bashrc` file.  
This ensures Conda is initialized correctly every time you start a new shell session.

```bash
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/network/rit/lab/basulab/Anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/network/rit/lab/basulab/Anaconda3/etc/profile.d/conda.sh" ]; then
        . "/network/rit/lab/basulab/Anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/network/rit/lab/basulab/Anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

---

## 2. Reload `.bashrc`

After editing `.bashrc`, reload it:

```bash
source ~/.bashrc
```

---

## 3. Disable Auto-activation of `base`

By default, Conda will auto-activate the `base` environment whenever a shell is opened.  
This is not recommended on shared HPC systems. Disable it with:

```bash
conda config --set auto_activate_base false
```

---

## 4. Configure Private Environment Directory

By default, new environments are created in the **shared folder**:
`/network/rit/lab/basulab/Anaconda3/envs/`

To avoid conflicts with other users, set your environments directory to your home folder.  
Run this command **once**:

```bash
conda config --add envs_dirs ~/.conda/envs
```

From now on, all your new environments will be stored under: 
`~/.conda/envs/`


## 5. Create a Conda Environment

Instead of manually listing packages, use the provided `environment.yml` file for reproducibility.

```bash
conda env create -f environment.yml
```

Check which environments exist using:
```bash
conda env list
```

Activate it with:

```bash
conda activate conus404
```

---

## 5. Register the Environment in JupyterLab

Once inside your environment, register its kernel so it is visible in **JupyterLab**:

```bash
python -m ipykernel install --user --name=conus404 --display-name "Python (conus404)"
```

---

✅ At this point, Conda is fully set up and ready to use on the HPC/DGX system.

---

# Starting Jupyter Server on HPC with Conda Environment

Once you have created and registered your Conda environment, you can run JupyterLab on the HPC.

---

## 1. Prepare the SLURM Job Script

Download the file `start_jupyter_notebook_hpc.slurm` into your working directory.

---

## 2. Submit the Job

From your working directory, submit the job:

```bash
sbatch start_jupyter_notebook_hpc.slurm
```

---

## 3. Check the Submitted Job ID

Use `sacct` to confirm that the job has started and to note the job ID:

```bash
sacct
```

Wait until the job status shows as **RUNNING**.

---

## 4. Retrieve the Jupyter URL

Once the job is running:

1. Go to the `slurmout/` folder inside your working directory.  
2. Open the file `jupyter-<jobid>.out`.  
3. Inside, you will find a link similar to:

   ```
   http://<node-host>:<port>/lab?token=<generated-token>
   ```

---

## 5. Connect from Your Browser

Copy the link and paste it into your browser.  
You now have access to JupyterLab running on the HPC with your Conda environment.

---

✅ That’s it! You are now running JupyterLab interactively on the HPC.

# Download CONUS404 Daily Data

This workflow uses helper scripts to download and organize **CONUS404 daily data** into yearly folders.

---

## 1. Required Files

Make sure the following files are present in your working directory:

- `conus404_daily_downloader.py`  
- `jobsub_conus_download.slurm`  
- `run_all_download.sh`  
- `run_all_redownload.sh`  

---

## 2. Customize Variables (if needed)

Inside **`conus404_daily_downloader.py`**, the default variables to download are:

```python
ds_sub = ds_all[["U10", "V10", "USHR6", "VSHR6", "SBCAPE", "MLCAPE", "MUCAPE"]].isel(**ny_indices)
```

- For reference, see CONUS404_variable_descriptions.txt for a complete list of available variables.

- Modify the variable list in conus404_daily_downloader.py as needed for your analysis.

## 3. Run the Main Download Script

Run the batch script to download all years (default: 1979–2022):

```bash
bash run_all_download.sh
```

- This will submit jobs for each year.

- Data will be downloaded into the folder: `/data/CONUS404/<year>/`

## 4. Re-run for Missing Files

If some files fail or are incomplete:

```bash
bash run_all_redownload.sh
```

This script checks for missing data and resubmits the jobs.

✅ At the end of this process, you will have a full set of daily CONUS404 data stored under /data/CONUS404/, organized by year.