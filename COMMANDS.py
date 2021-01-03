#argument names are in order
COMMANDS = {
    "findall": {
        "versions": {
            "all":{
                "id": 0,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "proximity":{
                "id": 1,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "relation": {
                "id": 2,
                "argument_num": 2,
                "argument_names": ['keyword', 'relation']
            }
        }
    },
    "get": {
        "versions":{
            "rdb":{
                "id": 3,
                "argument_num": 0,
                "argument_names": []
            }
        }
    }

}
