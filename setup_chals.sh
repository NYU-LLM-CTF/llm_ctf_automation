while getopts ":y:e:t:c:" opt
do
    case $opt in
        y)
        year="$OPTARG"
        # echo $year
        ;;
        e)
        event="$OPTARG"
        # echo $event
        ;;
        t)
        category="$OPTARG"
        # echo $category
        ;;
        c)
        chal="$OPTARG"
        # echo $chal
        ;;
        ?)
        echo "usage: -y {year} -e {event} -t {category} -c {challenge}"
        exit 1;;
    esac
done

chal_path="LLM_CTF_Database/$year/$event/$category/$chal"
cd $chal_path
echo "Building $d"
image_name=$(jq -r .name < challenge.json)
docker build -t "$image_name" "."