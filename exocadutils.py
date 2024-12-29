# This script loads the html file, and parses the <script ...> </script> tags in separate files.
# These files are then included in the original HTML with the src attribute.

from html.parser import HTMLParser
from openctm.bindings.python.openctm import *
import trimesh, ctypes, requests, base64, json, base64, os
from typing import List

class ScriptTagParser(HTMLParser):
    
    def __init__(self):
        super().__init__()
        self.tag_count = 0
        self.is_script_tag = False
        self.current_script_content = ''
        self.script_list = []

        
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            print("Encountered a start tag:", tag)
            self.is_script_tag = True
            

    def handle_endtag(self, tag):
        if tag == 'script':
            print("Encountered an end tag :", tag)
            self.is_script_tag = False
            self.tag_count += 1
            self.script_list.append(self.current_script_content)
            self.reset_current()
        
            
    def handle_data(self, data):
        if self.is_script_tag:
            self.current_script_content += data
            
    def get_script_list(self):
        return self.script_list

    def reset_current(self):
        self.is_script_tag = False
        self.current_script_content = ''



# async def extract_js_scripts(html_file_content) -> list[str]
# Extracts the JavaScript scripts from the HTML file and returns them as an array of strings
def extract_js_scripts(html_file_content: str) -> List[str]:
    parser = ScriptTagParser()
    parser.feed(html_file_content)
    return parser.get_script_list()


# async def extract_ctm_data(script_file_content) -> list[bytes]
# Extract CTM data from a string containing a JavaScript script and returns a list of bytes with
# the CTM data content (if any)
def extract_ctm_data(script_file_content: str) -> List[bytes]:
        
    # Find the line starting with "DentalWebGL.m_Data = "
    
    json_data = script_file_content.split('DentalWebGL.m_Data = {"data": "')[2].split('"}')[0]

    # Decode the base64-encoded data
    decoded_data = base64.b64decode(json_data)

    # Split the bytes array according to the byte sequence 0x4F 0x43 0x54 0x4D
    sequence = b'\x4F\x43\x54\x4D'
    split_data = decoded_data.split(sequence)
    # Re-append the sequence to each split data, apart for the first one
    ctm_data = [sequence + data for data in split_data[1:]]
    
    return ctm_data


# async def save_ctm_to_file(ctm_data: list[bytes], ctm_file_name:str)
# Saves the CTM data to a file
def save_ctm_to_file(ctm_data: List[bytes], ctm_file_path:str) -> None:
    with open(ctm_file_path, 'wb') as file:
        file.write(ctm_data)


# async def convert_ctm_to_mesh(ctm_file_name: str)
# Converts a CTM file to a mesh, using the CTM python binding
def convert_ctm_to_mesh(ctm_file_name: str) -> trimesh.Trimesh:
    
    ctm = ctmNewContext(CTM_IMPORT)
    mesh = ctmLoad(ctm, ctypes.c_char_p(ctm_file_name.encode()))
    err = ctmGetError(ctm)
    if err != CTM_NONE:
        print("Error loading file: " + str(ctmErrorString(err)))
        sys.exit()
    else:
        print("File loaded successfully")
        

    # Print information
    print("       Comment: " + str(ctmGetString(ctm, CTM_FILE_COMMENT)))
    print("Triangle count: " + str(ctmGetInteger(ctm, CTM_TRIANGLE_COUNT)))
    print("  Vertex count: " + str(ctmGetInteger(ctm, CTM_VERTEX_COUNT)))

    # Get vertices and faces from the mesh
    vertices = ctmGetFloatArray(ctm, CTM_VERTICES) # This is a pointer
    faces = ctmGetIntegerArray(ctm, CTM_INDICES) # This is a pointer

    # Retrieve arrays from the pointers
    vertices_ptr = ctypes.cast(vertices, ctypes.POINTER(CTMfloat))
    vertices = [vertices_ptr[i] for i in range(3 * ctmGetInteger(ctm, CTM_VERTEX_COUNT))]
    # Group the vertices into triplets
    vertices = [vertices[i:i+3] for i in range(0, len(vertices), 3)]

    # Retrieve arrays from the pointers
    faces_ptr = ctypes.cast(faces, ctypes.POINTER(CTMuint))
    faces = [faces_ptr[i] for i in range(3 * ctmGetInteger(ctm, CTM_TRIANGLE_COUNT))]
    # Group the faces into triplets
    faces = [faces[i:i+3] for i in range(0, len(faces), 3)]



    # Create mesh from vertices and faces
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

    return mesh

# async def save_mesh_to_file(mesh, stl_file_name)
def save_mesh_to_file(mesh: trimesh.Trimesh, stl_file_name: str) -> None:
    mesh.export(stl_file_name)

        
