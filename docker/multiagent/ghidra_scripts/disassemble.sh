#!/bin/bash

GHIDRA_ANALYZE="/opt/ghidra/ghidra_11.0.1_PUBLIC/support/analyzeHeadless"
GHIDRA_SCRIPTS="/opt/ghidra/customScripts"
DECOMPILE="DecompileToJson.java"
DISASSEMBLE="DisassembleToJson.java"

binary=$1
if [ ! -f "${binary}" ]
then
    echo "File not found ${binary}"
    exit 1
fi

tmp=$(mktemp -d)
${GHIDRA_ANALYZE} ${tmp} DummyProj -scriptpath ${GHIDRA_SCRIPTS} -import ${binary} \
    -postscript ${DISASSEMBLE} ${tmp}/output.json > ${tmp}/run.log 2>&1


if [ -f "${tmp}/output.json" ]
then
    cat ${tmp}/output.json
else
    echo "Output file not generated, error in disassembly!"
    cat ${tmp}/run.log
    exit 1
fi
