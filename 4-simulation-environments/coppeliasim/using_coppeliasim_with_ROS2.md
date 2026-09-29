# ROS2 with CoppeliaSim
 
### Set your Python environment

In the `usrset.txt` file, set the Python path. Ensure you have ROS2 and SAS installed on your system.

<img width="800" alt="image" src="https://github.com/user-attachments/assets/f601cad1-6ce8-4e91-b6a6-fa9b1d2e2f10" />


> [!TIP]
> To know where your `usrset.txt` file is, type this in the Lua commander
> ```shell
> sim.getStringParam(sim.stringparam_usersettingsdir)
> ```

> [!NOTE]
> In this example, we use a virtual environment to install the dependencies.
> Create a virtual environment
>
> ```shell
> cd ~
> python3 -m venv coppeliasim_venv
> ```
> 
> Activate the venv
> ```shell
> cd ~
> source coppeliasim_venv/bin/activate
> ```
>
> Install dependencies
>
>
> ```shell
> cd ~ /coppeliasim_venv/bin
> python3 -m pip install pyzmq cbor2 dqrobotics setuptools pyyaml

Now, modify the `usrset.txt` file to 

```python3
defaultPython = /home/juanjqo/coppeliasim_venv/bin/python3 // e.g. c:/Python38/python.exe
```
