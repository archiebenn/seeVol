# Development Log 

```
Project: seeVol
Author: Archie Benn sj19031@bristol.ac.uk  
Date started: 26-10-2026
```

--------- current to do list -----------

- look into Dijkstra's Algorithm for diagonals (26 neighbours per voxel instead of 6)  
- look into computing whole graph spatial values - this only takes on coordinate but could build to work across the whole graph (adjacent to the full `visibility_score()` at each voxel)  
- try to setup surface version as an option (ecologically relevant for my phd)  
- (eventually) set up spatial and visibility graph metrics in C++  
-----------------e----------------------

--------- current ideas or applications -----------

- what could comparing visibility <-> spatial metrics help identify? could be a genuine metric for turtuoisity of the tunnels and nest layout  
-----------------e----------------------

## Goal of this project  

- My PhD will involve using microCT scanning of excavated ant nests to gain a 3D image of their architecture  
- I want to quantify the accessibility, both visual and spatial, of different areas within the nests from these scans to investigate nest architecture development under different pressures, such as pathogen presence and different temperatures  
- I have started this `seevol` project as a tool to help me answer different and new questions about ant nest architecture. Its overall aim is to build on the current field and how zones within 3D structures can be quantified with respect to visibility via line-of-sight and spatial accessibility  
- However, I also want to develop a more general tool which can be used by others, be it in ecology or other areas working with complex 3D structures    
- So this project aims to be as open as possible, utilising `.npy` objects to generate spatial and visibility graphs, alongside visualisations of these metrics in `pyvista`     

## Tool pipeline goal (as of october 2026)  

- Aim of the tool is as follows:  

```
1. Raw microCT scans converted to volumes  
2. Volumes thresholded to binary (0 = solid/soil, 1 = open/excavated)  
3. Convert these volumes to `.npy` data type  
4. Load into python and tun `wise_pears` on the `.npy`  
5. `wise_pears` will run an occlusion-based pairwise ray-tracing algorithm between open voxels  
6. If a pair is occluded by a closed voxel, pair-wise 'is_visible' == 0 
7. If not occluded, pair-wise 'is_visible' == 1    
8. This algorithm will run using a C++ algorithm, accessed by python via `pybind11`  
9. Output of C++ function will return a visibility score between 0-1 for every open voxel in the volume  
10. From these scores, a visibility visualiser can be formed (coloured by visibility) using `pyvista`  
11. Also, a visibility graph from `networkx` can be formed too  
12. Tool will return both of these as the output for further analysis  
```

## Main issues  

- scaling issue: as this is currently set to be pairwise, comparisons between voxels will scale as O(n_open_voxels^2)  
- for large scans of nests at high resolution, this will massively increase compute expense   
- therefore need to implement in a tight loop in C++ and optimise using known solutions (to-do)  
- already going to use the Amanitides & Woo algorithm, but could think of some pair-wise solutions too  

### 26-10-2026  

- started development of `wise-pears` (`seevol`)  
- set up python project development and learned about how to create these pip-installable tools
- tested out using `pyvista` with some generated simple 3D binary volumes with 'solid voxel == 0' and 'open voxel == 1'  

### 28-10-26  

- generated `intricate_volumes.py` which uses `random` module and a set of defined rules to excavate out random volumes from a set full volume size
- the idea is to generate some intricate test volumes which are similar to ant nests for the development of the visibility graph  
- e.g here is a 200x200x200 excavated volume, visualised in `pyvista`, from:
  ```
  c = tunnel_excavater(size=200, seed=3, n_steps=200000, branch_prob=0.0001, radius=1)
  ```
  
![200 cubed](https://github.com/archiebenn/wise-pears/blob/main/images/test_200cubed.png "Test 200^3 excavated volume")

- got the core `is_visible()` function for a single pair visibility using Amanatides & Woo algorithm in `woo_test.cpp` working  
- then developed the main visible_pairs function which loops over every set of open voxel pairs (in one direction only) and tests with is_visible, returning a Nx3 array of open voxel coords and a Mx2 array of visible pair indices for that Nx3 array  
- this will allow both the visualisation with `pyvista` and the development ot `networkx` visibility graphs to be worked on, as the coordinates of each voxel and the visibility to each other open voxel from that one is saved  
- started on a test run for colouring `pyvista` outputs by a visibility score. here is an example on a 100^3 volume:  

![100 cubed](https://github.com/archiebenn/wise-pears/blob/main/images/pyvista_100cubed.png "Test 200^3 excavated volume")


- also did some benchmarking timings and got upt to around 70s for the 100^3 volume  
- the current C++ script can definitely be optimised further, e.g multithreading  

### 29-10-26  

- got claude to translate my C++ script line for line into Python, just to test benchmarking  
- (this is for the visible pairs calculation)  
- here is an example of the speed-up from implementing in C++ on a 45^3 volume:  

```
open voxels: 7416  edges: 125340
C++:    0.22159s
Python: 18.12656s  (82x slower)
```

- so can see how much extra time this would add for large volumes, and this is still single thread on C++  
- went over some pytests with Claude too as good to have for development  
- realised my C++ algorithm treats a ray passing exactly through a diagonal where one corner is solid treats the ray line as visible, which is not that strict -> could leave it as-is as not a very large issue but need to explicitly mention corner-grazing behaviour  
- want to look into other ways of reducing computation - need to add multithreading on outer loop and should speed up  
- added multithreading with help from Claude  
- 10.5x speed up on 100^3 macbook which is great, but then tried to do 150^3 and had memory errors  
- need to decide whether i want to fix that and allow bigger volumes or just have a hard limit on open voxel counts in volume  

### 30-10-26  

- changed from `pyvista` to `napari` and added as an optional install  
- so users can do `uv pip install visivox[gui]` and that will then install my dependencies + `napari[all]`  
- napari seems to be much better than pyvista, it renders full volumes and more interactive than `pyvista`  
- had an idea to try and optimise the ray counts: if a ray A<->B is visible, and C,D,E are all traversed by that ray, is there a way to mark B,C,E as visible from A and B too? then don't need to individually check/cast C,D,E from A or B. should speed it up if i can get it implemented somehow, but maybe not  

### 2-11-26  

- worked a bit on the actual render and decided to switch back to `pyvista` from `napari` as it is actually better  
- changed it to render the maximum visibility score from each 'viewing angle' in `pyvista`  
- this then only shows the highest visibility voxel for every angle/view which produces a much clearer visual in the render  
- also added wireframe mesh around each open voxel to explicitly show the full volume as the low visibility score voxels were very faint and hard to see  
- example output from a `porespy` - generated volume:  

![porespy](https://github.com/archiebenn/wise-pears/blob/main/images/porespy.png "64^3 Porespy example volume")

- also changed some of the excavation/volume generator in `generate_volumes.py` to have a downward bias to make it more ant-like  
- example of a 100^3 downward-bias excavation volume with visibility:  

![my excavation](https://github.com/archiebenn/wise-pears/blob/main/images/downard_bias.png "100^3 ant excavation example volume")

- and an example of a 150^3 and more realistic nest (slight increase in x (+ and -) and y (- only) excavation biases):  

![my excavation2](https://github.com/archiebenn/wise-pears/blob/main/images/realistic_nest.png "150^3 ant excavation example volume")

- had thoughts over the weekend and think i will try to apply octree and also some radius bounds for checking rays  
- radius bounds should theoretically allow much larger voxel counst to be checked as will stop it being O(n^2)  
- this is the current bottleneck as it limits any larger nests over like 125x125x125 currently  
- however memory issue may also be a bottleneck as currently storing 2 arrays (Nx3, Mx2) for all visible pairs and coords in C++ function  
- added a clear terminal output to see how far through the C++ loop the program is while running which really helps to estimate how long it might run for, e.g:  

```
VOXEL RAY-CASTING RUNNING
[########################################] 100%
```

## 3-11-26

- overall, volume visibility side is working well up to about 250-400k ooen voxels in a tunnel-like structure, and less for more open structures due to non-early exiting  
- i want to eventually publish this in JOSS or a similar journal, so i have decided i want to continue working on ti and build it up more as a useable tool  
- one idea is to compute proper graph analysis metrics in C++, rather than via networkx or igraph later which would probably break anyway  
- also to add spatial network analysis as another .cpp file: so will redistribute the current .cpp into different ones e.g.  common.cpp (shared), visibility.cpp (current occlusion.cpp mainly), spatial.cpp (spatial network analysis) and bindings.cpp (for python bindings)  
- did the above  
- also added `visibility_score()` which is similar to `visible_pairs()` but does not store array of pair, so uses much, much less memory on large open volumes. only useful for the visualisation though as graph metrics still require `visible_pairs()`  

## 4-11-26  

- spent most of the morning and early afternoon setting up the core/primitive spatial side of `seevol` with a BFS algorithm  
- this is breadth first search and is used in graph theory to search the shortest path of edges between two nodes  
- `spatial.cpp` was made and i set up `bfs_distances()` which takes input of a single open voxel coordinate and runs BFS to every single other reachable open voxel in the volume + returns a Nx3 coordinate array of open voxels and N, array distances to each from theh starting voxel (distance is -1 if unreachable)  
- this is good but BFS doesn't allow spatial movements in the diagonal as only sets neighbour as each of the outward facing 6 faces from each current voxel  
- can look into Dijkstra's Algorithm for diagonals (26 neighbours per voxel instead of 6)  
- and also look into computing whole graph spatial values - this only takes on coordinate but could build to work across the whole graph (adjacent to the full `visibility_score()` at each voxel)  
- i also would like to have an option to apply spatial stuff to surface volumes only, as this is only really feasible option for ants, but also keep the full version for other uses  
- also, as `seevol` is now two main branches: visibility and spatial, a third one to consider in the future could be airflow. a simple lattice diffusion model across the voxels could work well at scale potentially (p sure libs exist already or could build on spatial BFS anyway)    

## 5-11-26

- added BFS shortest path function in C++ (similar to full BFS but saves parent voxel at each step + retraces at end)  
- implemented this as a visualiser function in python too  
- now here are the three current main functions of `seevol`, run an an identical 200x200x200 volume:  

#### All-voxel visibility from ray traversal (Amanatides-Woo):  

![200^3](https://github.com/archiebenn/wise-pears/blob/main/images/05-11-vis.png "All-voxel visibility from ray traversal (Amanatides-Woo)")

#### BFS all-voxel distances from a single start voxel:  

![200^3](https://github.com/archiebenn/wise-pears/blob/main/images/05-11-bfs-all.png "BFS all-voxel distances from a single start voxel")

#### Shortest path between two voxels (using BFS path):  

![200^3](https://github.com/archiebenn/wise-pears/blob/main/images/05-11-bfs-shortest.png "shortest path between two voxels (using BFS path)")


## 7-11-26  

- current cloc: 

```
cloc --exclude-lang=HTML,TeX,JavaScript,CSS .

-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
C++                              4            196            309            482
Python                          15            226            247            464
Markdown                         3            107              0            209
CSV                              1              0              0             44
TOML                             1              8              0             38
make                             1              4              0             38
YAML                             1              6              1             35
SVG                              1              0              0             28
CMake                            1              5              6             25
C/C++ Header                     3             18             80             21
XML                              1              0              0             13
-------------------------------------------------------------------------------
SUM:                            32            570            643           1397
-------------------------------------------------------------------------------
```

## 8-11-26  

- updated the main code headers and some functions to add MIT and clearer function names  
- also going to go in and clear up a lot of my comments  
- changed claude to be less explicit in giving me answers today and more as a guide to places where i can find them/solve issues more myself, as i am concerned about using AI so much in my understanding of the code/being able to question 'why was this done?'  
- formatted with these two commands (run whenever from root):  
```
# python formatting (across full repo)
uv run ruff format .

# cpp formatting (only in src/)
find src -regex '.*\.\(cpp\|hpp\)' -exec clang-format -i {} \;
```