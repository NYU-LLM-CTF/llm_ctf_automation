# LLM CTF Automation Guide

We have two GitHub repositories: LLM_CTF_Database and llm_ctf_automation. 
[LLM_CTF_Database](https://github.com/sj2790/LLM_CTF_Database) repository contains all CTF challenges we used for our experiments. 
The [llm_ctf_automation](https://github.com/NickNameInvalid/llm_ctf_automation) repository is the framework needed for conducting the experiments.

**Step 1**

You would need to get both repositories on your local machine following the instructions below. First, you would need to clone the [llm_ctf_automation](https://github.com/NickNameInvalid/llm_ctf_automation) repository using the following command: 
```bash git clone git@github.com:NickNameInvalid/llm_ctf_automation.git```
Once you do this, you would need to enter this llm_ctf_automation repository you just cloned using the command ```cd llm_ctf_automation```. 
Now that you are inside the framework's repository, you can clone the [LLM_CTF_Database](https://github.com/sj2790/LLM_CTF_Database) repository with all the challenges. You can do this using the following command: ```bash git clone git@github.com:sj2790/LLM_CTF_Database.git.```

**Step 2**

Install python environment according to the requirements.txt. One way you can do this is using conda environment with the following command: ```conda create -n llm_ctf python=3.11```.

**Step 3**

Setup docker container with setup.sh. ```bash setup.sh```

**Step 4**

Finish the whole setup using the do_eval.sh file. You can do this using the following command: ```bash do_eval.sh```