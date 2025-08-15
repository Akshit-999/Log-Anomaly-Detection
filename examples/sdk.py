# Install the Lightning SDK
# pip install -U lightning-sdk

# login to the platform
# export LIGHTNING_USER_ID=c5b49cf3-be59-4ce4-a979-05797cdfb3e8
# export LIGHTNING_API_KEY=02d25854-7a0d-415d-a4b1-90676fd4364e

from lightning_sdk import Machine, Studio, JobsPlugin, MultiMachineTrainingPlugin

# Start the studio
s = Studio(name="my-sdk-studio", teamspace="language-model", org="akshitagrawal999", create_ok=True)
print("starting Studio...")
s.start()

# prints Machine.CPU-4
print(s.machine)

print("switching Studio machine...")
s.switch_machine(Machine.A10G)

# prints Machine.A10G
print(s.machine)

# prints Status.Running
print(s.status)

print(s.run("nvidia-smi"))

print("Stopping Studio")
s.stop()

# duplicates Studio, this will also duplicate the environment and all files in the Studio
duplicate = s.duplicate()

# delete original Studio, duplicated Studio is it's own entity and not related to original anymore
s.delete()

# stop and delete duplicated Studio
duplicate.stop()
duplicate.delete()
    