MODEL="$1"
for f in logs/*/*/*/*.${MODEL}.*.json ; 
do outdir=./public_html/$(dirname "$f") ; 
mkdir -p "$outdir" ; outname="$(basename "$f")" ; 
outname="${outname/.json/.html}"; echo "$f" ; 
python ./llm_ctf/dump_commands.py "$f" | ansi2html -l -s osx | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "$outdir"/"$outname" ; done