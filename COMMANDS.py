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
            },
            "reccurence":{
                "id": 11,
                "argument_num": 2,
                "argument_names": ['keyword', 'occurence']
            }
        }
    },
    "get": {
        "versions":{
            "rdb":{
                "id": 3,
                "argument_num": 0,
                "argument_names": []
            },
            "proximity":{
                "id": 4,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "doubles":{
                "id": 5,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "triples":{
                "id": 6,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "quadruples":{
                "id": 7,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "quintuples":{
                "id": 8,
                "argument_num": 1,
                "argument_names": ['keyword']
            },
            "filtered":{
                "id": 9,
                "argument_num": 1,
                "argument_names": ['keyword']
            }   
        }
    }
}
