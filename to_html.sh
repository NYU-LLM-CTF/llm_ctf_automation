# MODEL="$1"
# for f in logs/*/*/*/*/*.${MODEL}.*.json ; 
# do outdir=./html/$(dirname "$f") ; 
# mkdir -p "$outdir" ; outname="$(basename "$f")" ; 
# outname="${outname/.json/.html}"; echo "$f" ; 
# python ./llm_ctf/dump_commands.py "$f" | ansi2html -l | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "$outdir"/"$outname" ; done
python ./llm_ctf/dump_commands.py "/home/ms12416/projects/llm_ctf_automation/logs/ms12416/NYU_Baseline_0_LLM_CTF_Dataset_Dev_0/2023q-rev-baby_s_third.json" | ansi2html -l | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "html"/"log.html"