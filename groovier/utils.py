def concat_args(args): 
    response = ""
    for i, arg in enumerate(args): 
        if i > 0: 
            response = response + " " + arg
        else: 
            response = arg
    return response