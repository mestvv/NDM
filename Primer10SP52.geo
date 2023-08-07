// Gmsh project created on Sun Aug 06 11:35:59 2023
SetFactory("OpenCASCADE");
//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {0.15, 0, 0, 1.0};
//+
Recursive Delete {
  Point{2}; 
}
//+
Point(2) = {0, 0.29, 0, 1.0};
//+
Point(3) = {-0.075, 0.32, 0, 1.0};
//+
Point(4) = {-0.075, 0.4, 0, 1.0};
//+
Symmetry {1, 0, 0, 1} {
  Duplicata { Point{4}; Point{3}; Point{2}; Point{1}; }
}
//+
Recursive Delete {
  Point{5}; Point{7}; Point{6}; Point{8}; 
}
//+
Translate {0.15, 0, 0} {
  Point{1}; Point{2}; 
}
//+
Translate {-0.15, 0, 0} {
  Duplicata { Point{2}; Point{1}; }
}
//+
Translate {0.3, 0, 0} {
  Duplicata { Point{4}; Point{3}; }
}
//+
Line(1) = {6, 1};
//+
Line(2) = {1, 2};
//+
Line(3) = {2, 8};
//+
Line(4) = {8, 7};
//+
Line(5) = {7, 4};
//+
Line(6) = {4, 3};
//+
Line(7) = {5, 3};
//+
Line(8) = {5, 6};
//+
Curve Loop(1) = {8, 1, 2, 3, 4, 5, 6, -7};
//+
Plane Surface(1) = {1};
//+
Physical Surface("Concrete", 9) = {1};
//+
Point(9) = {0.3, 0.3, 0, 1.0};
//+
Recursive Delete {
  Point{9}; 
}
//+
Point(9) = {0.03, 0.03, 0, 1.0};
//+
Point(10) = {0.03, 0.06, 0, 1.0};
//+
Point(11) = {0.12, 0.03, 0, 1.0};
//+
Physical Point("RebarD18", 10) = {10, 9, 11};
//+
Rotate {{0, 1, 0}, {0, 0, 0}, -0.244978663} {
  Surface{1}; Point{10}; Point{9}; Point{11}; Curve{1}; Curve{2}; Curve{8}; Curve{5}; Curve{6}; Curve{7}; Curve{3}; Curve{4}; 
}
//+
Rotate {{0, 1, 0}, {0, 0, 0}, 0.244978663} {
  Point{9}; Point{10}; Point{11}; Point{13}; Point{14}; Curve{1}; Curve{2}; Curve{3}; Surface{1}; Point{12}; Point{19}; Point{18}; Point{15}; Point{16}; Point{17}; Curve{8}; Curve{7}; Curve{4}; Curve{5}; Curve{6}; 
}
//+
Rotate {{1, 0, 0}, {0, 0, 0}, 0.244978663} {
  Point{10}; Point{11}; Point{13}; Point{14}; Point{9}; Point{25}; Point{20}; Point{24}; Point{21}; Point{22}; Point{23}; Curve{2}; Curve{1}; Curve{8}; Curve{7}; Curve{3}; Curve{4}; Curve{5}; Curve{6}; Surface{1}; 
}
//+
Rotate {{1, 0, 0}, {0, 0, 0}, -0.244978663} {
  Point{10}; Point{11}; Point{13}; Point{14}; Point{9}; Point{25}; Point{20}; Point{24}; Point{21}; Point{22}; Point{23}; Curve{2}; Curve{8}; Curve{1}; Curve{7}; Curve{3}; Curve{4}; Curve{5}; Curve{6}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, 0.244978663} {
  Point{10}; Point{11}; Point{13}; Point{14}; Point{9}; Point{25}; Point{20}; Point{24}; Point{21}; Point{22}; Point{23}; Curve{2}; Curve{1}; Curve{8}; Curve{7}; Curve{3}; Curve{4}; Curve{5}; Curve{6}; Surface{1}; 
}
//+
Physical Point("RebarD18", 11) = {10, 9, 11};
//+
Physical Point(" RebarD18", 10) -= {10, 9, 11};
//+
Physical Point("RebarD18", 11) = {10, 9, 11};
//+
MeshSize {20, 10, 11, 13, 14, 9, 21, 22, 23, 25, 24} = 0.05;
//+
MeshSize {25, 9, 24, 23, 22, 21, 20, 14, 13, 11, 10} = 0.01;
//+
Rotate {{0, 1, 0}, {0, 0, 0}, 0.24497866312686} {
  Point{25}; Point{9}; Point{24}; Point{23}; Point{22}; Point{21}; Point{20}; Point{14}; Point{13}; Point{11}; Point{10}; Curve{8}; Curve{7}; Curve{6}; Curve{5}; Curve{4}; Curve{3}; Curve{2}; Curve{1}; Surface{1}; 
}
//+
Rotate {{0, 1, 0}, {0, 0, 0}, -0.24497866312686} {
  Point{13}; Point{20}; Point{25}; Point{24}; Point{10}; Point{9}; Point{21}; Point{11}; Point{23}; Point{22}; Point{14}; Curve{7}; Curve{8}; Curve{1}; Curve{6}; Curve{4}; Curve{5}; Curve{2}; Curve{3}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, 0.24497866312686} {
  Point{20}; Point{21}; Point{22}; Point{23}; Point{24}; Point{25}; Point{10}; Point{9}; Point{11}; Point{13}; Point{14}; Curve{6}; Curve{7}; Curve{5}; Curve{8}; Curve{4}; Curve{1}; Curve{2}; Curve{3}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, -0.24497866312686} {
  Point{20}; Point{21}; Point{22}; Point{23}; Point{24}; Point{25}; Point{10}; Point{11}; Point{9}; Point{14}; Point{13}; Curve{6}; Curve{5}; Curve{4}; Curve{7}; Curve{8}; Curve{3}; Curve{2}; Curve{1}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, -0.24497866312686} {
  Point{20}; Point{21}; Point{22}; Point{23}; Point{24}; Point{25}; Point{10}; Point{9}; Point{11}; Point{13}; Point{14}; Curve{6}; Curve{7}; Curve{5}; Curve{8}; Curve{4}; Curve{1}; Curve{2}; Curve{3}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, 0.24497866312686} {
  Point{20}; Point{21}; Point{22}; Point{23}; Point{24}; Point{25}; Point{10}; Point{9}; Point{11}; Point{13}; Point{14}; Curve{6}; Curve{7}; Curve{5}; Curve{8}; Curve{4}; Curve{1}; Curve{2}; Curve{3}; Surface{1}; 
}
//+
Rotate {{0, 0, 1}, {0, 0, 0}, -0.2449786629951} {
  Point{25}; Point{9}; Point{24}; Point{23}; Point{22}; Point{21}; Point{20}; Point{14}; Point{13}; Point{11}; Point{10}; Curve{8}; Curve{7}; Curve{6}; Curve{5}; Curve{4}; Curve{3}; Curve{2}; Curve{1}; Surface{1}; 
}
