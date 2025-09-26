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

## 4. Create a Conda Environment

You can now create your own Conda environment, with name **myenv**:

```bash
conda create -n myenv python numpy matplotlib xarray zarr netcdf4 h5netcdf hdf5 jupyterlab ipykernel
```

Activate it with:

```bash
conda activate myenv
```

---

## 5. Register the Environment in JupyterLab

Once inside your environment, register its kernel so it is visible in **JupyterLab**:

```bash
python -m ipykernel install --user --name=myenv --display-name "Python (myenv)"
```

---

✅ At this point, Conda is fully set up and ready to use on the HPC/DGX system.

---

# Starting Jupyter Server on HPC with Conda Environment

Once you have created and registered your Conda environment, you can run JupyterLab on the HPC.

---

## 1. Prepare the SLURM Job Script

Save the following script as `start_jupyter_notebook_hpc.slurm` in your working directory:

```bash
#!/bin/bash

#SBATCH --job-name=jupyter
#SBATCH --output=slurmout/jupyter-%j.out
#SBATCH --error=slurmout/jupyter-%j.err
#SBATCH --time=05-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32

# Ensure log directory exists
mkdir -p slurmout

# Load conda init script
source /network/rit/lab/basulab/Anaconda3/etc/profile.d/conda.sh
conda activate myenv

# Random port
port=$((RANDOM % 1000 + 8000))
token="$(openssl rand -hex 16)"

# Detect node hostname/IP
node_host=$(hostname -f)

# Print URL to .out
echo "=========================================================="
echo "Your Jupyter Lab session is available at:"
echo "   http://${node_host}:${port}/lab?token=${token}"
echo "=========================================================="

# Start Jupyter Lab
jupyter lab --no-browser --ip=0.0.0.0 --port=$port \
  --NotebookApp.token="${token}"
```

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