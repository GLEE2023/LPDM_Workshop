## LPDM - LunaSAT Power and Data Model
# Start here!
We are currently developing a model to simulate power and data consumption of LunaSats given different configurations of sensor modes. Ultimately this will be used by end users to experiment with different ways to collect data with their LunaSat.

Here is an example of what we have so far:
![preview](https://github.com/GLEE2023/LPDM/blob/main/modelFolder/images/chart_preview.png)

# How to use
This project is meant to be as configurable as possible. We will give you some options so you can play around with your own configurations, locally or on the cloud.
### Binder
You can go to this link if you want to access the notebook/ Python files in-browser. Be sure to download your notebook if you want to save changes!
[Jupyter Notebook on Binder](https://mybinder.org/v2/gh/GLEE2023/LPDM/tim)

### Local Machine
If you want to run the notebook or Python files on your local machine, you can follow these steps. 

First, make sure you have Python version 3.7 or above. Python 3.9 is recommended. You can download Python from [here](https://www.python.org/downloads/).

Next we are going to clone the LPDM repository and get access to its files. To do this you can run the following on the command line of your system (Terminal for MacOS & Unix, Powershell for Windows):

```console
  git clone https://github.com/GLEE2023/LPDM.git
  cd ModeUserInterface
```

Now that you have the repository on your local machine, we can create a virtual environment and activate it for the libraries required to run the model. To do this, you can run the following command:
For Mac users:
```console
  python3 -m venv name_of_env
  source name_of_env/bin/activate
```

Or if on Windows:
```console
  python -m venv <name_of_env>
  <name_of_env>/Scripts/activate.bat
```

Finally, we can run the following command to install the necessary packages and run the model notebook:
If you are on linux you may need to install pip seperately.
For Mac users:
```console
  python3 -m pip install -r requirements.txt
```
Or if on Windows:
```console
  python -m pip install -r requirements.txt
```

Now your environment is set up and ready to run the model code! If you are using VS Code, you should change the kernel of your notebook to your virtual environment name by opening the kernel manager in the top right while a notebook is open. If using Jupyter from the command line, be sure to change your kernel to the one labeled (ipykernel).

Jupyter is relatively simple to use and is recommended for making local changes to the LPDM.

