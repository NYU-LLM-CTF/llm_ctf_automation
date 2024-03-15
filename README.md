# LLM CTF Automation Guide

Two repositories are used to reproduce the whole experiment: LLM_CTF_Database and llm_ctf_automation. 
[LLM_CTF_Database](https://github.com/sj2790/LLM_CTF_Database) repository contains all CTF challenges we used for our experiments. 
The [llm_ctf_automation](https://github.com/NickNameInvalid/llm_ctf_automation) repository is the framework needed for conducting the experiments.

**Step 1**

Clone the [llm_ctf_automation](https://github.com/NickNameInvalid/llm_ctf_automation) repository using the following command: <br>
```bash git clone git@github.com:NickNameInvalid/llm_ctf_automation.git```
Enter the llm_ctf_automation repository you just cloned using the command  <br>
```cd llm_ctf_automation```. 
Clone the [LLM_CTF_Database](https://github.com/sj2790/LLM_CTF_Database) repository with all the challenges using the following command:  <br>
```bash git clone git@github.com:sj2790/LLM_CTF_Database.git.```

**Step 2**

Install python environment according to the requirements.txt. One way to do this is using conda environment with the following command:  <br>
```conda create -n llm_ctf python=3.11```.

**Step 3**

Setup docker container with setup.sh.  <br>
```bash setup.sh```

**Step 4**

Finish the whole setup using the do_eval.sh file. You can do this using the following command:  <br>
```bash do_eval.sh```
