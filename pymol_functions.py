from pymol import cmd,preset,util
import pandas as pd
import numpy as np

#Keep track of times elec_mag is called
count=1

def loadCSV(filename):
'''Arguments:
   filename (string): Name of the file to be opened


   Return value (dataframe): Dataframe of the CSV opened
'''
    data = pd.read_csv(filename)
    if data.empty:
        print("Dataframe is empty")
    else:
        print(data[['S','Electric Magnitude', 'Magnetic Magnitude','Cosine of Angle']])
    return data
cmd.extend("loadCSV", loadCSV)

def newLoad(filename):
'''Arguments:
    filename (string): Name of molecule file to be opened


    Return value: None
'''
    cmd.load(filename)
    # Everything ball and stick
    preset.ball_and_stick(selection="all", mode=1)

    # Change carbon color
    cmd.color("gray",selection="elem c")
    return
cmd.extend("newLoad",newLoad)

def str_to_list(string,internalType="float"):
 '''Arguments:
    string (string): String object to be converted to list of floats

    internalType (string): String indicating the type of list to be converted to


    Return value (list): Converted list of objects
'''
   if type(string) is list:
       return string
   newList=string.strip('][').split(',')
   if internalType=="float":
       newList=[float(n) for n in newList]
   return newList


def elec_mag(elec_end,mag_end,elec_scaling_factor=7, mag_scaling_factor=7, elec_start=[0.0,0.0,0.0],mag_start=[0.0,0.0,0.0]):
'''Arguments:
    elec_end (list of floats): Endpoint of electric vector

    mag_end (list of floats): Endpoint of magnetic vector

    elec_scaling_factor (int): Scaling factor for electric vector

    mag_scaling_factor (int): Scaling factor for magnetic vector

    elec_start (list of floats): Starting point for electric vector - defaults to coordinate origin [0,0,0]

    mag_start (list of floats): Starting point for magnetic vector - defaults to coordinate origin [0,0,0]


    Return value: None
'''
    global count
    elec_end=str_to_list(elec_end)
    temp_elec_end = elec_end.copy()
    if elec_start!='sele':
        elec_start=str_to_list(elec_start)
    #Use count to make a unique name for each arrow object,
    #allows multiple elec_mags to be spawned
    cgo_arrow(origin=elec_start,endpoint=temp_elec_end,type="electric",name=str(count), scaling=elec_scaling_factor)

    mag_end=str_to_list(mag_end)
    temp_mag_end = mag_end.copy()
    if mag_start!='sele':
        mag_start=str_to_list(mag_start)

    cgo_arrow(origin=mag_start,endpoint=temp_mag_end,type="magnetic",name=str(count),scaling=mag_scaling_factor)
    cmd.group(f"stilde{count}",members=f"electric{count} magnetic{count}")

    count+=1
    return
cmd.extend("elec_mag",elec_mag)


def elec_mag_fromAtom(elec_end,mag_end, elec_scale=7, mag_scale=7, elec_start='sele',mag_start='sele'):
    '''Arguments:
        elec_end (list of floats): Endpoint of electric vector

        mag_end (list of floats): Endpoint of magnetic vector

        elec_scale (int): Scaling factor for electric vector

        mag_scale (int): Scaling factor for magnetic vector

        elec_start (list of floats): Starting point for electric vector - defaults to coordinate origin [0,0,0]

        mag_start (list of floats): Starting point for magnetic vector - defaults to coordinate origin [0,0,0]


        Return value: None
    '''
    #Just calls the other function with appropriate args,
    #avoids repeating function body
    elec_mag(elec_end,mag_end,elec_start=elec_start,mag_start=mag_start, elec_scaling_factor=elec_scale, mag_scaling_factor=mag_scale)
    return
cmd.extend("elec_mag_fromAtom", elec_mag_fromAtom)


#Function can't (or at least shouldn't) access variables from inside
#other functions.
##If you want to make this default, can set df=None and call
##loadCSV with a set file in this case.
def select_vectors(index, df, fromAtom=False):
'''Arguments:
   index (int): Index of dataframe where vector data will be selected from

   df (Dataframe): Dataframe containing vector data loaded previously

   fromAtom (bool): Boolean indicating whether or not the vector will be drawn using an atom as origin


   Return value: List of lists containing electric vector at index 0, magnetic vector at index 1
'''
    index = int(index)
    cart=['X','Y','Z']
    ##Uses list comprehension to express more succinctly
    elecVec = [df.iloc[index]['Electric'+x] for x in cart]
    magVec = [df.iloc[index]['Magnetic'+x] for x in cart]
    vecList = [elecVec, magVec]
    if fromAtom is False:
        elec_mag(elecVec, magVec)
    else:
        elec_mag_fromAtom(elecVec,magVec)
    return vecList
cmd.extend("select_vectors",select_vectors)

#Want a worker function that automates this more
#e.g. calls loadCSV, then runs a loop of select_vectors and elec_mag
#for a particular list of indices.

def multiple_vectors(indices, df, fromAtom=False):
    '''Arguments:
       indices (List of int): Indices of dataframe where vector data will be selected from

       df (Dataframe): Dataframe containing vector data loaded previously

       fromAtom (bool): Boolean indicating whether or not the vector will be drawn using an atom as origin


       Return value: None
    '''
    for index in indices:
        vec = select_vectors(index, df, fromAtom)

cmd.extend("multiple_vectors", multiple_vectors)

def createSphere(pos, radius=1.0, color = 'Yellow',transparency=.5):
'''Arguments:
   pos (List of floats): Indicates the x,y,z coordinates for the sphere to be drawn at

   radius (Float): Radius of sphere - default 1.0

   color (string): Color of sphere - default yellow

   transparency (Float): transparency value of sphere - default .5

   Return value: None
'''
    cmd.set("cgo_sphere_quality", 4)
    radius=float(radius)
    pos = str_to_list(pos)
    obj = [cgo.SPHERE] + pos + [radius]
    cmd.load_cgo(obj,'s1',0)
    cmd.color(color,selection='s1')
    cmd.set("cgo_transparency",value=transparency,selection="s1")
cmd.extend("createSphere",createSphere)
