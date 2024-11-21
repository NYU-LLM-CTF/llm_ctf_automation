MODEL="$1"
for f in logs/*/*/*/*/*.${MODEL}.*.json ; 
do outdir=./html/$(dirname "$f") ; 
mkdir -p "$outdir" ; outname="$(basename "$f")" ; 
outname="${outname/.json/.html}"; echo "$f" ; 
python ./llm_ctf/dump_commands.py "$f" | ansi2html -l | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "$outdir"/"$outname" ; done