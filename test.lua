function printAkms(Akm)
  local Opp = Chop(NewOperator("CF",1,{0},Akm))
  print("\nAkm = ")
  print(Akm)
  print("\n Operator on basis of spherical Harmonics or Kubic Harmonics (same for s orbital as a matrix")
  print("s")
  print(Chop(OperatorToMatrix(Opp)))
end
 
function printAkmp(Akm)
  local t=sqrt(1/2)
  local u=I*sqrt(1/2)
  local rotmatKp   = {{ t, 0,-t },
                      { u, 0, u },
                      { 0, 1, 0 }}
  local Opp = Chop(NewOperator("CF",3,{0,1,2},Akm))
  print("\nAkm = ")
  print(Akm)
  print("\n Operator on basis of spherical Harmonics as a matrix")
  print("p_{-1},p_{0},p_{1}")
  print(Chop(OperatorToMatrix(Opp)))
  print("\n Operator on basis of Kubic Harmonics as a matrix")
  print("p_x, p_y, p_z")
  print(Chop(OperatorToMatrix(Rotate(Opp,rotmatKp))))
end
 
function printAkmd(Akm)
  local t=sqrt(1/2)
  local u=I*sqrt(1/2)
  local rotmatKd   = {{ t, 0, 0, 0, t },
                      { 0, 0, 1, 0, 0 },
                      { 0, u, 0, u, 0 },
                      { 0, t, 0,-t, 0 },
                      { u, 0, 0, 0,-u }}
  local Opp = Chop(NewOperator("CF",5,{0,1,2,3,4},Akm))
  print("\nAkm = ")
  print(Akm)
  print("\n Operator on basis of spherical Harmonics as a matrix")
  print("d_{-2},d_{-1},d_{0},d_{1},d_{2}")
  print(Chop(OperatorToMatrix(Opp)))
  print("\n Operator on basis of Kubic Harmonics as a matrix")
  print("d_{x^2-y^2},d_{z^2},d_{yz},d_{xz},d_{xy}")
  print(Chop(OperatorToMatrix(Rotate(Opp,rotmatKd))))
end
 
function printAkmf(Akm)
  local t=sqrt(1/2)
  local u=I*sqrt(1/2)
  local d=sqrt(3/16)
  local q=sqrt(5/16)
  local e=I*sqrt(3/16)
  local r=I*sqrt(5/16)
  local rotmatKf   = {{ 0, u, 0, 0, 0,-u, 0 },
                      { q, 0,-d, 0, d, 0,-q },
                      {-r, 0,-e, 0,-e, 0,-r },
                      { 0, 0, 0, 1, 0, 0, 0 },
                      {-d, 0,-q, 0, q, 0, d },
                      {-e, 0, r, 0, r, 0,-e },
                      { 0, t, 0, 0, 0, t, 0 }}
  local Opp = Chop(NewOperator("CF",7,{0,1,2,3,4,5,6},Akm))
  print("\nAkm = ")
  print(Akm)
  print("\n Operator on basis of spherical Harmonics as a matrix")
  print("f_{-3},f_{-2},f_{-1},f_{0},f_{1},f_{2},f_{3}")
  print(Chop(OperatorToMatrix(Opp)))
  print("\n Operator on basis of Kubic Harmonics as a matrix")
  print("f_{xyz},f_{5x^3-3x},f_{5y^3-3y},f_{5z^3-3z},f_{x(y^2-z^2)},f_{y(z^2-x^2)},f_{z(x^2-y^2)}")
  print(Chop(OperatorToMatrix(Rotate(Opp,rotmatKf))))
end
 
 
 
 
 
print("\nl=2 D4h")
Eeg=1
Et2g=2
Akm = PotentialExpandedOnClm("D4h",2,{Eeg,Et2g})
printAkmd(Akm)
 



