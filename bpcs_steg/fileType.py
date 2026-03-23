def get_file_type(filename: str) -> tuple[bool, str, str, str, str]:
    f = open(filename, "rb")
    filetype = ""
    header = ""
    trailer = ""
    likely = ""

    found = False 

    #get first 8B of file 
    header_8B = f.read(8).hex()

    #ms office (97-2003) files have subheaders at offset 512B to identify the file type
    f.seek(512)
    offset512 = f.read(8).hex()
    f.close()

    #print(filename, header_8B)

    #old ms office
    if header_8B == "d0cf11e0a1b11ae1":
        #subheaders
        if offset512[0:8] == "eca5c100":
            filetype = ".doc"
            header = "eca5c100"        
        elif offset512 == "fdffffff20000000":
            filetype = ".xls"
            header = "fdffffff20000000"
        elif offset512[0:8] == "fdffffff":
            filetype = ".ppt"
            header = "fdffffff"

        likely = ".doc"
        found = True
    
    #new ms office 
    if header_8B[0:16] == "504b030414000600":
        likely = ".docx"
        header = header_8B[0:16]
        trailer = "504b0506"
        found = True

    #zip - zip file header is the same as the first 4B of the ms office headers
    elif header_8B[0:8] == "504b0304":
        filetype = ".zip"
        header = header_8B[0:8]
        found = True
    
    #png
    if header_8B[0:16] == "89504e470d0a1a0a":
        filetype = ".png"
        header = header_8B[0:16]
        trailer = "49454e44Ae426082"
        found = True 
    
    #pdf
    if header_8B[0:8] == "25504446":
        filetype = ".pdf"
        header = header_8B[0:8]
        trailer = "0d0a2525454f460d0A"
        likely = ".pdf"
        found = True 

    #mp3
    if header_8B[0:6] == "494433":
        filetype = ".mp3"
        header = header_8B[0:6]
        found = True 

    #jpg
    if header_8B[0:4] == "ffd8":
        filetype = ".jpg"
        header = header_8B[0:4]
        trailer = "ffd9"
        found = True 

    if found == False: 
        filetype = ".txt"
    
    return found, filetype, header, trailer, likely 



if __name__ == "__main__":

    print("Get file type")
    
