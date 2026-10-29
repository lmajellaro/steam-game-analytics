# ======== Helper functions ========

#############################################
# Read and format SQL script from file      #
#############################################
def load_sql(file_path, **params):
    with open(file_path, "r") as f:
        query = f.read()
    return query.format(**params)