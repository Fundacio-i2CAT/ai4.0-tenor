#!/bin/bash

declare tenor_ip
declare mongo_ip
declare cassandra_address
declare logger_address
CURRENT_PROGRESS=0
bold=$(tput bold)
normal=$(tput sgr0)

show_menus() {
	clear
	echo "       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNo,. ..:kMMMMMMMMMMMMMMMMMMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMk    .    .NMMMMMMMMMMMMMMMMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0    OMM:   .MMMMMMMMMMMMMMMMMMMM
       MMMMMMW.         ,x        0X    ;MMM.   oM;   .MMMK    OM.     ..;oNMMMMMMM
       MMMMMMW'..    ...cx    ....KK     dMM.   lM.   ;MMMN    dM.   .,.    OMMMMMM
       MMMMMMMMMM.   cMMMx    XMMMMK      0M.   lM'   ,MMMX    kM.   cMMl   .MMMMMM
       MMMMMMMMMM.   cMMMx    lddkMK      .N.   lMd    XMMo    NM.   cMN,   ;MMMMMM
       MMMMMMMMMM.   cMMMx       'MK    '  ;.   lMM;   .c;    OMM.    .   .oWMMMMMM
       MMMMMMMMMM.   cMMMx    0XXNMK    0;      lMMMx'      :KMMM.   ..   kMMMMMMMM
       MMMMMMMMMM.   cMMMx    XMMMMK    0W.     lMNNNNXOkk0NNNNWM.   cN.   dMMMMMMM
       MMMMMMMMMM.   cMMMx    ....XK    0MX.    lMocccccccccccc0M.   cMX    oMMMMMM
       MMMMMMMMMM,...oMMMk........XX....KMM0....dMxooooooooooooKM'...oMM0....dMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
       MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    echo "       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	echo "1. Install TeNOR"
	echo "2. Reconfigure configuration files"
	echo "3. Register microservices"
	echo "4. Add new PoP (Deprecated - Please, use the User Interface at http://localhost:9000)"
	echo "5. Remove PoP (Deprecated - Please, use the User Interface at http://localhost:9000)"
	echo "6. Inserting sample VNF and NS"
	echo "7. Exit"
}
function delay()
{
    sleep 0.2;
}
function progress()
{
    PARAM_PROGRESS=$1;
    PARAM_STATUS=$2;

    if [ $CURRENT_PROGRESS -le 0 -a $PARAM_PROGRESS -ge 0 ]  ; then echo -ne "[..........................] (0%)  $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 5 -a $PARAM_PROGRESS -ge 5 ]  ; then echo -ne "[#.........................] (5%)  $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 10 -a $PARAM_PROGRESS -ge 10 ]; then echo -ne "[##........................] (10%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 15 -a $PARAM_PROGRESS -ge 15 ]; then echo -ne "[###.......................] (15%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 20 -a $PARAM_PROGRESS -ge 20 ]; then echo -ne "[####......................] (20%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 25 -a $PARAM_PROGRESS -ge 25 ]; then echo -ne "[#####.....................] (25%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 30 -a $PARAM_PROGRESS -ge 30 ]; then echo -ne "[######....................] (30%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 35 -a $PARAM_PROGRESS -ge 35 ]; then echo -ne "[#######...................] (35%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 40 -a $PARAM_PROGRESS -ge 40 ]; then echo -ne "[########..................] (40%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 45 -a $PARAM_PROGRESS -ge 45 ]; then echo -ne "[#########.................] (45%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 50 -a $PARAM_PROGRESS -ge 50 ]; then echo -ne "[##########................] (50%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 55 -a $PARAM_PROGRESS -ge 55 ]; then echo -ne "[###########...............] (55%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 60 -a $PARAM_PROGRESS -ge 60 ]; then echo -ne "[############..............] (60%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 65 -a $PARAM_PROGRESS -ge 65 ]; then echo -ne "[#############.............] (65%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 70 -a $PARAM_PROGRESS -ge 70 ]; then echo -ne "[###############...........] (70%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 75 -a $PARAM_PROGRESS -ge 75 ]; then echo -ne "[#################.........] (75%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 80 -a $PARAM_PROGRESS -ge 80 ]; then echo -ne "[####################......] (80%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 85 -a $PARAM_PROGRESS -ge 85 ]; then echo -ne "[#######################...] (90%) $PARAM_PHASE \r"  ; delay; fi;
    if [ $CURRENT_PROGRESS -le 90 -a $PARAM_PROGRESS -ge 90 ]; then echo -ne "[##########################] (100%) $PARAM_PHASE \r" ; delay; fi;
    if [ $CURRENT_PROGRESS -le 100 -a $PARAM_PROGRESS -ge 100 ];then echo -ne 'Done!                                            \n' ; delay; fi;

    CURRENT_PROGRESS=$PARAM_PROGRESS;

}

pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}

installTenor(){
	echo "Installing TeNOR..."

	echo "Checking the Ruby version: " $RUBY_VERSION
	ruby_version=`ruby -e "print(RUBY_VERSION < '2.2.0' ? '1' : '0' )"`
	if [[ ! `which ruby` ]]; then
        echo "Ruby is not installed, please install a version higer than 2.2.0."
        pause
        return
    fi
    if [ $ruby_version -eq 1 ]; then
        ruby --version > /dev/null 2>&1
        RUBY_IS_INSTALLED=$?
        echo "Ruby version: " $RUBY_VERSION
        echo "Please, install a ruby version higher or equal to 2.2.0"
        pause
        return
    fi
    if [[ ! `which bundle` ]]; then
        echo "Bundler is not installed, please install it."
        pause
        return
    fi

    printf "\n\n${bold}Starting TeNOR installation... Please wait, this can take some time.${normal}\n\n"

    declare -a tenor_ns_url=("ns_manager" "ns_provisioner" "nsd_validator" "ns_monitoring" "ns_catalogue" "sla_enforcement" )
    declare -a tenor_vnf_url=("vnf_manager" "vnf_provisioner" "vnfd_validator" "vnf_monitoring" "vnf_catalogue" )

    count=0
    max=15
    progress 0

    bundle install --quiet
    count=$((count+1))
    progress  $(( 100 * $count / $max )) ""

    array=(*/)
    for folder in "${array[@]}"; do
        #printf "$folder\n"

        if [[ "$folder" =~ ^ns-* ]] || [[ "$folder" =~ ^vnf-* ]] || [[ "$folder" =~ ^hot-* ]] || [[ "$folder" = "ui/" ]]; then
            cd $folder

            if [ "$folder" = "ns-manager/" ]; then
                cd default/monitoring
                bundle install --quiet
                cd ../../
            fi
            bundle install --quiet
            cd ../
            count=$((count+1))
            progress  $(( 100 * $count / $max )) ""
        fi
    done

    fluent-gem install fluent-plugin-mongo

    configureFiles

    printf "\n\n${bold}TeNOR installation script finished${normal}\n\n"
    exit
}

configureIps(){
    RAILS_ENV=development
    TENOR_IP="127.0.0.1"
    MONGODB_IP="127.0.0.1:27017"
    CASSANDRA_ADDRESS="127.0.0.1"
    LOGGER_ADDRESS="127.0.0.1:24224"

    echo -e "Please, insert the IPs and ports used in each service. ${bold}You can press [ENTER] without write anything in the case of local installation.${normal}\n\n"

    echo "Type the IP where is installed TeNOR, followed by [ENTER]:"
    read tenor_ip
    if [ -z "$tenor_ip" ]; then tenor_ip=$TENOR_IP; fi

    echo "Type the IP:PORT (xxx.xxx.xxx.xxx:xxxx) where is installed the MongoDB, followed by [ENTER]:"
    read mongo_ip
    if [ -z "$mongo_ip" ]; then mongo_ip=$MONGODB_IP; fi

    echo "Type the IP (xxx.xxx.xxx.xxx) where is installed Cassandra, followed by [ENTER]:"
    read cassandra_address
    if [ -z "$cassandra_address" ]; then cassandra_address=$CASSANDRA_ADDRESS; fi

    logger_host=${LOGGER_ADDRESS%%:*}
    logger_port=${LOGGER_ADDRESS##*:}

    mongodb_host=${mongo_ip%%:*}
    mongodb_port=${mongo_ip##*:}

    mkdir -p fluentd
    cat >fluentd/fluent.conf <<EOL
    # In v1 configuration, type and id are @ prefix parameters.
    # @type and @id are recommended. type and id are still available for backward compatibility

    ## built-in TCP input
    ## $ echo <json> | fluent-cat <tag>
    <source>
      @type forward
      @id forward_input
    </source>

    ## built-in UNIX socket input
    #<source>
    #  @type unix
    #</source>

    # HTTP input
    # http://localhost:8888/<tag>?json=<json>
    <source>
      @type http
      @id http_input

      port 8888
    </source>

    ## File input
    ## read apache logs with tag=apache.access
    #<source>
    #  @type tail
    #  format apache
    #  path /var/log/httpd-access.log
    #  tag apache.access
    #</source>

    # Listen HTTP for monitoring
    # http://localhost:24220/api/plugins
    # http://localhost:24220/api/plugins?type=TYPE
    # http://localhost:24220/api/plugins?tag=MYTAG
    <source>
      @type monitor_agent
      @id monitor_agent_input

      port 24220
    </source>

    # Listen DRb for debug
    <source>
      @type debug_agent
      @id debug_agent_input

      bind 127.0.0.1
      port 24230
    </source>

    ## match tag=debug.** and dump to console
    <match debug.**>
      @type stdout
      @id stdout_output
    </match>

    <match **>
      @type mongo
      host ${mongodb_host}
      port ${mongodb_port}
      database ns_manager
      #collection tenor_logs
      tag_mapped

      # for capped collection
      capped
      capped_size 64m

      # authentication
      # user mongouser
      # password mongouser_pass

      # flush
      flush_interval 10s
    </match>

EOL

}
configureFiles(){
    printf "\nConfiguring NS/VNF modules\n\n"

    configureIps

    rm **/config/config.yml

    for folder in $(find . -type d  \( -name "ns*" -o -name "vnf*" -o -name "hot-generator" \) ); do
        printf "$folder\n"
        cd $folder

        if [ ! -f config/config.yml ]; then
            cp config/config.yml.sample config/config.yml
        fi
        if [ -f config/mongoid.yml.sample ] &&  [ ! -f config/mongoid.yml ]; then
            cp config/mongoid.yml.sample config/mongoid.yml
        fi
        if [ -f config/database.yml.sample ] &&  [ ! -f config/database.yml ]; then
            cp config/database.yml.sample config/database.yml
        fi

        sed -i -e 's/\(logger_host:\).*/\1 '$logger_host'/' config/config.yml
        sed -i -e 's/\(logger_port:\).*/\1 '$logger_port'/' config/config.yml
        for i in "${tenor_ns_url[@]}"; do
            sed  -i -e  's/\('$i':\).*\:\(.*\)/\1 '$tenor_ip':\2/' config/config.yml
        done
        for i in "${tenor_vnf_url[@]}"; do
            sed  -i -e  's/\('$i':\).*\:\(.*\)/\1 '$tenor_ip':\2/' config/config.yml
        done

        if [ -f config/mongoid.yml ]; then
            sed -i -e 's/127.0.0.1:27017/'$mongo_ip'/' config/mongoid.yml
        fi
        if [ -f config/database.yml ]; then
            sed -i -e 's/127.0.0.1:27017/'$cassandra_address'/' config/database.yml
        fi
        if [ "$folder" = "./ns-monitoring" ]; then
          rake db:migrate
        fi
        if [ "$folder" = "./ns-manager" ]; then
          echo "Generating admin user."
            cd default/monitoring
            if [ ! -f config/config.yml ]; then
                cp config/config.yml.sample config/config.yml
            fi
            cd ../../
        fi

        cd ../
    done

    printf "\nConfiguring UI...\n\n"
    cp ui/app/config.js.sample ui/app/config.js

    printf "\nConfiguration done.\n\n"
    pause
}

addNewPop(){
    echo "Adding new PoP..."
    TENOR_HOST=localhost:4000
    OPENSTACK_NAME=default
    OPENSTACK_IP=localhost
    ADMIN_TENANT_NAME=admin
    KEYSTONEPASS=password
    KEYSTONEUSER=admin
    OPENSTACK_DNS=8.8.8.8

    echo -e "Please, insert the IPs and ports used requested. ${bold}You can press [ENTER] without write anything in the case of local installation.${normal}\n\n"

    echo "Type the address where TeNOR is RUNNING (localhost:4000), followed by [ENTER]:"
    read tenor_host
    if [ -z "$tenor_host" ]; then tenor_host=$TENOR_HOST; fi

    echo "Type the Openstack name, followed by [ENTER]:"
    read openstack_name
    if [ -z "$openstack_name" ]; then openstack_name=$OPENSTACK_NAME; fi

    echo "Type the Openstack IP, followed by [ENTER]:"
    read openstack_ip
    if [ -z "$openstack_ip" ]; then openstack_ip=$OPENSTACK_IP; fi

    echo "Type the Openstack name, followed by [ENTER]:"
    read keystoneUser
    if [ -z "$keystoneUser" ]; then keystoneUser=$KEYSTONEUSER; fi

    echo "Type the Openstack password, followed by [ENTER]:"
    read -s keystonePass
    if [ -z "$keystonePass" ]; then keystonePass=$KEYSTONEPASS; fi

    echo "Type the Openstack tenant name, followed by [ENTER]:"
    read admin_tenant_name
    if [ -z "$admin_tenant_name" ]; then admin_tenant_name=$ADMIN_TENANT_NAME; fi

    echo "Type true or false if the Openstack user is admin, followed by [ENTER]:"
    read admin_tenant_name
    if [ -z "$admin_user_type" ]; then admin_user_type=$ADMIN_TENANT_NAME; fi

    echo "Type the Openstack DNS IP, followed by [ENTER]:"
    read openstack_dns
    if [ -z "$openstack_dns" ]; then openstack_dns=$OPENSTACK_DNS; fi

    response=$(curl -XPOST http://$tenor_host/pops/dc -H "Content-Type: application/json" \
    -d '{"msg": "PoP Testbed", "dcname":"'$openstack_name'", "isAdmin": "'$admin_user_type'" "adminid":"'$keystoneUser'","password":"'$keystonePass'", "extrainfo":"pop-ip='$openstack_ip' tenant-name='$admin_tenant_name' keystone-endpoint=http://'$openstack_ip':35357/v2.0 orch-endpoint=http://'$openstack_ip':8004/v1 compute-endpoint=http://'$openstack_ip':8774/v2.1 neutron-endpoint=http://'$openstack_ip':9696/v2.0 dns='$openstack_dns'"}')

    echo -e "\n\n"
    echo $response
    echo -e "\n\n"
    pause
}

conn_openstack() {
    tokenId=$(curl -XPOST $1":35357/v2.0" -d "" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["token"]["id"]')

}

removePop() {
    echo "Removing PoP..."
    tenor_host=localhost:4000

    curl -XGET http://$tenor_host/pops/dc  | ruby -r rubygems -r json -e "puts JSON[STDIN.read];"

    echo "Type the PoP Id, followed by [ENTER]:"
    read pop_id

    curl -XGET http://$tenor_host/gatekeeper/dc/$pop_id  | ruby -r rubygems -r json -e "puts JSON[STDIN.read];"

    echo "Are you sure you want to remove this PoP (y/n)?, followed by [ENTER]:"
    read remove

    if [ "$remove" = "y" ]; then
      echo "Removing PoP..."
      curl -XDELETE http://$tenor_host/gatekeeper/dc/$pop_id
    fi

    pause
}

registerMicroservice(){
    echo "Register new microservice..."
    echo "No implemented yet!."
    pause
}

insertSamples(){
    echo "Inserting VNF..."
    vnf_id=$(curl -XPOST localhost:4000/vnfs -H "Content-Type: application/json" --data-binary @vnfd-validator/assets/samples/vnfd_example.json | ruby -r rubygems -r json -e "puts JSON[STDIN.read]['vnfd']['id'];")
    echo "Inserting NS..."
    ns_id=$(curl -XPOST localhost:4000/network-services -H "Content-Type: application/json" --data-binary @nsd-validator/assets/samples/nsd_example.json | ruby -r rubygems -r json -e "puts JSON[STDIN.read]['nsd']['id'];")
    echo "NSD id: " $ns_id
    echo "VNFD id: " $vnf_id

    pause
}
read_options(){

    if [ -n "$1" ]; then
        choice=$1
    else
        local choice
	    read -p "${bold}Enter choice [ 1 - 7 ]${normal} " choice
    fi

	case $choice in
		1) installTenor ;;
		2) configureFiles ;;
		3) registerMicroservice ;;
		4) addNewPop ;;
		5) removePop ;;
		6) insertSamples ;;
		7) exit 0;;
		*) echo -e "${RED}Error...${STD}" && sleep 2
	esac
}

# ----------------------------------------------
# Step #3: Trap CTRL+C, CTRL+Z and quit singles
# ----------------------------------------------
trap '' SIGINT SIGQUIT SIGTSTP

# -----------------------------------
# Step #4: Main logic - infinite loop
# ------------------------------------

choice=$1

while true
do
	show_menus
	read_options $choice
	exit 0
done
