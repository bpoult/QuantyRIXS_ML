-- Helper functions
function Split(s, delimiter)
    result = {};
    for match in (s..delimiter):gmatch("(.-)"..delimiter) do
        table.insert(result, match);
    end
    return result;
end

function find_file_with_extension(extension)
    local handle
    
    -- Try different OS commands
    if package.config:sub(1,1) == '\\' then
        -- Windows
        handle = io.popen('dir /b *.' .. extension .. ' 2>nul')
    else
        -- Unix/Linux/Mac
        handle = io.popen('ls *.' .. extension .. ' 2>/dev/null')
    end
    
    if handle then
        local result = handle:read("*l")
        handle:close()
        return result
    end
    return nil
end
---------------------------------------------------------
-- Input
config_name = find_file_with_extension("inp_quanty")
--split_config = Split(config_name,'.')
name,ext = config_name:match'([^.]*).(.*)'

print('Quanty configuration file ' .. config_name)
print(' ')
for line in io.lines(config_name) do
  --print(line)
  if line ~= '' and string.sub(line,0,1) ~= '#' then
    local x = Split(line,' ')
    print(line)
    if x[1] == 'NPsi_Initial' then
      -- this parameter is not used in Greens function calc.
      NPsi_Initial = tonumber(x[3])
    end
    if x[1] == 'NPsi_Final' then
      -- this parameter is not used in Greens function calc.
      NPsi_Final = tonumber(x[3])
    end
    if x[1] == 'tenDq_3d_i' then
      tenDq_3d_i = tonumber(x[3])
    end
    if x[1] == 'tenDq_3d_f' then
      tenDq_3d_f = tonumber(x[3])
    end
    if x[1] == 'Ds_3d_i' then
      Ds_3d_i = tonumber(x[3])
    end
    if x[1] == 'Ds_3d_f' then
      Ds_3d_f = tonumber(x[3])
    end
    if x[1] == 'Dt_3d_i' then
      Dt_3d_i = tonumber(x[3])
    end
    if x[1] == 'Dt_3d_f' then
      Dt_3d_f = tonumber(x[3])
    end
    if x[1] == 'scalef2_3d3d_i' then
      scalef2_3d3d_i = tonumber(x[3])
    end
    if x[1] == 'scalef2_3d3d_f' then
      scalef2_3d3d_f = tonumber(x[3])
    end
    if x[1] == 'scalef4_3d3d_i' then
      scalef4_3d3d_i = tonumber(x[3])
    end
    if x[1] == 'scalef4_3d3d_f' then
      scalef4_3d3d_f = tonumber(x[3])
    end
    if x[1] == 'scalef2_2p3d' then
      scalef2_2p3d = tonumber(x[3])
    end
    if x[1] == 'scaleg' then
      scaleg = tonumber(x[3])
    end
    if x[1] == 'scale_3dSOC_i' then
      scale_3dSOC_i = tonumber(x[3])
    end
    if x[1] == 'scale_3dSOC_f' then
      scale_3dSOC_f = tonumber(x[3])
    end
    if x[1] == 'scale_2pSOC' then
      scale_2pSOC = tonumber(x[3])
    end
    if x[1] == 'U_3d_3d_i' then
      U_3d_3d_i = tonumber(x[3])
    end
    if x[1] == 'U_3d_3d_f' then
      U_3d_3d_f = tonumber(x[3])
    end
    if x[1] == 'U_2p_3d_f' then
      U_2p_3d_f = tonumber(x[3])
    end
    if x[1] == 'E_2p' then
      E_2p = tonumber(x[3])
    end
  end
end
print(' ')

-- spec_config_name = 'CoTerpy_2026_03_12.inp_rixs'
spec_config_name = find_file_with_extension("inp_rixs")


--split_config = Split(config_name,'.')
name,ext = spec_config_name:match'([^.]*).(.*)'

print('Spectra configuration file ' .. spec_config_name)
print(' ')
for line in io.lines(spec_config_name) do
  --print(line)
  if line ~= '' and string.sub(line,0,1) ~= '#' then
    local x = Split(line,' ')
    print(line)
    if x[1] == 'initial_state' then
      initial_state = tonumber(x[3])
    end
    if x[1] == 'energy_start' then
      energy_start = tonumber(x[3])
    end
    if x[1] == 'energy_end' then
      energy_end = tonumber(x[3])
    end
    if x[1] == 'energy_step' then
      energy_step = tonumber(x[3])
    end
    if x[1] == 'loss_start' then
      loss_start = tonumber(x[3])
    end
    if x[1] == 'loss_step' then
      loss_step = tonumber(x[3])
    end
    if x[1] == 'loss_end' then
      loss_end = tonumber(x[3])
    end
    if x[1] == 'FWHM_lorentz1' then
      Gamma1_L3 = tonumber(x[3])
    end
    if x[1] == 'FWHM_lorentz1b' then
      Gamma1_L2 = tonumber(x[3])
    end
    if x[1] == 'L3_L2_split' then
      L3_L2_split = tonumber(x[3])
    end
    if x[1] == 'FWHM_lorentz2' then
      Gamma2 = tonumber(x[3])
    end
  end
end
-- Gamma2 check:
if Gamma2 < 0.0001 then
  loss_step = 0.002
  Gamma2 = 0.01
  print('FWHM_lorentz2 is 0, new values:')
  print(string.format('loss_step = %4.3f', loss_step))
  print(string.format('FWHM_lorentz2 = %3.2f', Gamma2))
end
print(' ')


NF=16
NB=0
IndexDn_2p={0,2,4}
IndexUp_2p={1,3,5}
IndexDn_3d={6,8,10,12,14}
IndexUp_3d={7,9,11,13,15}
 
-- just like in the previous example we define several operators acting on the Ni -3d shell
 
OppSx   =NewOperator("Sx"   ,NF, IndexUp_3d, IndexDn_3d)
OppSy   =NewOperator("Sy"   ,NF, IndexUp_3d, IndexDn_3d)
OppSz   =NewOperator("Sz"   ,NF, IndexUp_3d, IndexDn_3d)
OppSsqr =NewOperator("Ssqr" ,NF, IndexUp_3d, IndexDn_3d)
OppSplus=NewOperator("Splus",NF, IndexUp_3d, IndexDn_3d)
OppSmin =NewOperator("Smin" ,NF, IndexUp_3d, IndexDn_3d)
 
OppLx   =NewOperator("Lx"   ,NF, IndexUp_3d, IndexDn_3d)
OppLy   =NewOperator("Ly"   ,NF, IndexUp_3d, IndexDn_3d)
OppLz   =NewOperator("Lz"   ,NF, IndexUp_3d, IndexDn_3d)
OppLsqr =NewOperator("Lsqr" ,NF, IndexUp_3d, IndexDn_3d)
OppLplus=NewOperator("Lplus",NF, IndexUp_3d, IndexDn_3d)
OppLmin =NewOperator("Lmin" ,NF, IndexUp_3d, IndexDn_3d)
 
OppJx   =NewOperator("Jx"   ,NF, IndexUp_3d, IndexDn_3d)
OppJy   =NewOperator("Jy"   ,NF, IndexUp_3d, IndexDn_3d)
OppJz   =NewOperator("Jz"   ,NF, IndexUp_3d, IndexDn_3d)
OppJsqr =NewOperator("Jsqr" ,NF, IndexUp_3d, IndexDn_3d)
OppJplus=NewOperator("Jplus",NF, IndexUp_3d, IndexDn_3d)
OppJmin =NewOperator("Jmin" ,NF, IndexUp_3d, IndexDn_3d)
 
Oppldots=NewOperator("ldots",NF, IndexUp_3d, IndexDn_3d)
 
-- as in the previous example we define the Coulomb interaction
 
OppF0 =NewOperator("U", NF, IndexUp_3d, IndexDn_3d, {1,0,0})
OppF2 =NewOperator("U", NF, IndexUp_3d, IndexDn_3d, {0,1,0})
OppF4 =NewOperator("U", NF, IndexUp_3d, IndexDn_3d, {0,0,1})
 
-- as in the previous example we define the crystal-field operator
 
Akm = PotentialExpandedOnClm("Oh",2,{0.6,-0.4})
OpptenDq = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, Akm)
 
-- and as in the previous example we define operators that count the number of eg and t2g
-- electrons
 
Akm = PotentialExpandedOnClm("Oh",2,{1,0})
OppNeg = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, Akm)
Akm = PotentialExpandedOnClm("Oh",2,{0,1})
OppNt2g = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, Akm)
 
-- new for core level spectroscopy are operators that define the interaction acting on the
-- Ni-2p shell. There is actually only one of these interactions, which is the Ni-2p
-- spin-orbit interaction
 
Oppcldots= NewOperator("ldots", NF, IndexUp_2p, IndexDn_2p)
 
-- we also need to define the Coulomb interaction between the Ni 2p- and Ni 3d-shell
-- Again the interaction (e^2/(|r_i-r_j|)) is expanded on spherical harmonics. For the interaction
-- between two shells we need to consider two cases. For the direct interaction a 2p electron
-- scatters of a 3d electron into a 2p and 3d electron. The radial integrals involve
-- the square of a 2p radial wave function at coordinate 1 and the square of a 3d radial
-- wave function at coordinate 2. The transfer of angular momentum can either be 0 or 2.
-- These processes are called direct and the resulting Slater integrals are F[0] and F[2].
-- The second proces involves a 2p electron scattering of a 3d electron into the 3d shell
-- and at the same time the 3d electron scattering into a 2p shell. These exchange processes
-- involve radial integrals over the product of a 2p and 3d radial wave function. The transfer
-- of angular momentum in this case can be 1 or 3 and the Slater integrals are called G1 and G3.
 
-- In Quanty you can enter these processes by labeling 4 indices for the orbitals, once
-- the 2p shell with spin up, 2p shell with spin down, 3d shell with spin up and 3d shell with
-- spin down. Followed by the direct Slater integrals (F0 and F2) and the exchange Slater 
-- integrals (G1 and G3)
 
-- Here we define the operators separately and later sum them with appropriate prefactors
 
OppUpdF0 = NewOperator("U", NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1,0}, {0,0})
OppUpdF2 = NewOperator("U", NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0,1}, {0,0})
OppUpdG1 = NewOperator("U", NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0,0}, {1,0})
OppUpdG3 = NewOperator("U", NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0,0}, {0,1})
 
-- next we define the dipole operator. The dipole operator is given as epsilon.r
-- with epsilon the polarization vector of the light and r the unit position vector
-- We can expand the position vector on (renormalized) spherical harmonics and use
-- the crystal-field operator to create the dipole operator. 
 
-- x polarized light is defined as x = Cos[phi]Sin[theta] = sqrt(1/2) ( C_1^{(-1)} - C_1^{(1)})
Akm = {{1,-1,sqrt(1/2)},{1, 1,-sqrt(1/2)}}
TXASx = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm)
-- y polarized light is defined as y = Sin[phi]Sin[theta] = sqrt(1/2) I ( C_1^{(-1)} + C_1^{(1)})
Akm = {{1,-1,sqrt(1/2)*I},{1, 1,sqrt(1/2)*I}}
TXASy = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm)
-- z polarized light is defined as z = Cos[theta] = C_1^{(0)}
Akm = {{1,0,1}}
TXASz = NewOperator("CF", NF, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm)


-- x polarized light is defined as x = Cos[phi]Sin[theta] = sqrt(1/2) ( C_1^{(-1)} - C_1^{(1)})
Akm = {{1,-1,sqrt(1/2)},{1, 1,-sqrt(1/2)}}
T3d2px = NewOperator('CF', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm)
-- y polarized light is defined as y = Sin[phi]Sin[theta] = sqrt(1/2) I ( C_1^{(-1)} + C_1^{(1)})
Akm = {{1,-1,sqrt(1/2)*I},{1, 1,sqrt(1/2)*I}}
T3d2py = NewOperator('CF', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm)
-- z polarized light is defined as z = Cos[theta] = C_1^{(0)}
Akm = {{1,0,1}}
T3d2pz = NewOperator('CF', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm)
 
-- we now define rotation matrices that rotate the basis of (l lz s sz) to a basis of
-- (k tau s sz) for the d-shell or (j jz) for the p-shell. The function rotate calculates
-- R^* Opp R^T and the rotation matrix is thus equal to the eigen-functions of the
-- crystal-field operator and the spin-orbit coupling operator respectively.
 
-- the total matrix is a 16 by 16 matrix
 
t=sqrt(1/2)
u=I*sqrt(1/2)
d=sqrt(1/3)
e=sqrt(2/3)
 
-- rotating the 2p states to a (j jz) basis
 
rotmatjjzp = {{ 0,-e, d, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0,-d, e, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 1, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, d, e, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, e, d, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 1,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
              { 0, 0, 0, 0, 0, 0,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 1, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 1, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 1, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 1, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 1, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 1}}
 
-- rotating the 3d states to a (k tau s sz) basis
 
rotmatKd   = {{ 1, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 1, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 1, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 1, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 1, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 1,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
              { 0, 0, 0, 0, 0, 0,     t, 0, 0, 0, 0, 0, 0, 0, t, 0},
              { 0, 0, 0, 0, 0, 0,     0, t, 0, 0, 0, 0, 0, 0, 0, t},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, u, 0, 0, 0, u, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, u, 0, 0, 0, u, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, t, 0, 0, 0,-t, 0, 0, 0},
              { 0, 0, 0, 0, 0, 0,     0, 0, 0, t, 0, 0, 0,-t, 0, 0},
              { 0, 0, 0, 0, 0, 0,     u, 0, 0, 0, 0, 0, 0, 0,-u, 0},
              { 0, 0, 0, 0, 0, 0,     0, u, 0, 0, 0, 0, 0, 0, 0,-u}}
 
-- We can modify the rotation of the 2p orbitals such that we only
-- keep the j=1/2 sub-shell
 
rotmatjjzp12 = {{ 0,-e, d, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0,-d, e, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
                { 0, 0, 0, 0, 0, 0,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 1, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 1, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 1, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 1, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 1, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 1}}
 
-- or modify it such that we only keep the j=3/2 sub-shell
 
rotmatjjzp32 = {{ 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 1, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, d, e, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, e, d, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 1,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
                { 0, 0, 0, 0, 0, 0,     1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 1, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 1, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 1, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 1, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 1, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 1}}
 
-- We can modify the rotation of the 3d orbitals such that we only keep
-- the orbitals belonging to the eg irreducible representation.
 
rotmatKdeg   = {{ 1, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 1, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 1, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 1, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 1, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 1,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
                { 0, 0, 0, 0, 0, 0,     t, 0, 0, 0, 0, 0, 0, 0, t, 0},
                { 0, 0, 0, 0, 0, 0,     0, t, 0, 0, 0, 0, 0, 0, 0, t},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}
 
-- or such that we only keep the orbitals belonging to the t2g irreducible representation
 
rotmatKdt2g  = {{ 1, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 1, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 1, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 1, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 1, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 1,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
 
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, u, 0, 0, 0, u, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, u, 0, 0, 0, u, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, t, 0, 0, 0,-t, 0, 0, 0},
                { 0, 0, 0, 0, 0, 0,     0, 0, 0, t, 0, 0, 0,-t, 0, 0},
                { 0, 0, 0, 0, 0, 0,     u, 0, 0, 0, 0, 0, 0, 0,-u, 0},
                { 0, 0, 0, 0, 0, 0,     0, u, 0, 0, 0, 0, 0, 0, 0,-u}}
			
 
-- The transition operator restricted to a subset of orbitals is then given as:
-- Tnew = R2^* . R1^* . Told . R1^T . R2^T
-- with R1 the restricted rotation matrix
-- and R2 the full rotation matrix conjugate transposed (R^+)
 
TXASxj12 = Chop(Rotate(Chop(Rotate(TXASx,rotmatjjzp12)),ConjugateTranspose(rotmatjjzp)))
TXASyj12 = Chop(Rotate(Chop(Rotate(TXASy,rotmatjjzp12)),ConjugateTranspose(rotmatjjzp)))
TXASzj12 = Chop(Rotate(Chop(Rotate(TXASz,rotmatjjzp12)),ConjugateTranspose(rotmatjjzp)))
TXASxj32 = Chop(Rotate(Chop(Rotate(TXASx,rotmatjjzp32)),ConjugateTranspose(rotmatjjzp)))
TXASyj32 = Chop(Rotate(Chop(Rotate(TXASy,rotmatjjzp32)),ConjugateTranspose(rotmatjjzp)))
TXASzj32 = Chop(Rotate(Chop(Rotate(TXASz,rotmatjjzp32)),ConjugateTranspose(rotmatjjzp)))
TXASxeg  = Chop(Rotate(Chop(Rotate(TXASx,rotmatKdeg  )),ConjugateTranspose(rotmatKd  )))
TXASyeg  = Chop(Rotate(Chop(Rotate(TXASy,rotmatKdeg  )),ConjugateTranspose(rotmatKd  )))
TXASzeg  = Chop(Rotate(Chop(Rotate(TXASz,rotmatKdeg  )),ConjugateTranspose(rotmatKd  )))
TXASxt2g = Chop(Rotate(Chop(Rotate(TXASx,rotmatKdt2g )),ConjugateTranspose(rotmatKd  )))
TXASyt2g = Chop(Rotate(Chop(Rotate(TXASy,rotmatKdt2g )),ConjugateTranspose(rotmatKd  )))
TXASzt2g = Chop(Rotate(Chop(Rotate(TXASz,rotmatKdt2g )),ConjugateTranspose(rotmatKd  )))

T3d2pxeg = ConjugateTranspose(TXASxeg)
T3d2pyeg = ConjugateTranspose(TXASyeg)
T3d2pzeg = ConjugateTranspose(TXASzeg)
T3d2pxt2g = ConjugateTranspose(TXASxt2g)
T3d2pyt2g = ConjugateTranspose(TXASyt2g)
T3d2pzt2g = ConjugateTranspose(TXASzt2g)

-- initialize Hamiltonian
H_i = 0
H_f = 0 


-- Define the atomic term.
N_2p = NewOperator('Number', NF, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NF, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_3d = NewOperator('Number', NF, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NF, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

F0_3d_3d = NewOperator('U', NF, IndexUp_3d, IndexDn_3d, {1, 0, 0})
F2_3d_3d = NewOperator('U', NF, IndexUp_3d, IndexDn_3d, {0, 1, 0})
F4_3d_3d = NewOperator('U', NF, IndexUp_3d, IndexDn_3d, {0, 0, 1})

F0_2p_3d = NewOperator('U', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
F2_2p_3d = NewOperator('U', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
G1_2p_3d = NewOperator('U', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
G3_2p_3d = NewOperator('U', NF, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

F2_3d_3d_i = 12.663 * scalef2_3d3d_i
F4_3d_3d_i = 7.917 * scalef4_3d3d_i
F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

F2_3d_3d_f = 13.422 * scalef2_3d3d_f
F4_3d_3d_f = 8.395 * scalef4_3d3d_f
F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
F2_2p_3d_f = 7.900 * scalef2_2p3d
G1_2p_3d_f = 5.951 * scaleg
G3_2p_3d_f = 3.385 * scaleg
F0_2p_3d_f = U_2p_3d_f + 1 / 15 * G1_2p_3d_f + 3 / 70 * G3_2p_3d_f

H_i = H_i + Chop(
  F0_3d_3d_i * F0_3d_3d
  + F2_3d_3d_i * F2_3d_3d
  + F4_3d_3d_i * F4_3d_3d)

H_f = H_f + Chop(
  F0_3d_3d_f * F0_3d_3d
  + F2_3d_3d_f * F2_3d_3d
  + F4_3d_3d_f * F4_3d_3d
  + F0_2p_3d_f * F0_2p_3d
  + F2_2p_3d_f * F2_2p_3d
  + G1_2p_3d_f * G1_2p_3d
  + G3_2p_3d_f * G3_2p_3d)

ldots_3d = NewOperator('ldots', NF, IndexUp_3d, IndexDn_3d)

ldots_2p = NewOperator('ldots', NF, IndexUp_2p, IndexDn_2p)

zeta_3d_i = 0.074 * scale_3dSOC_i

zeta_3d_f = 0.092 * scale_3dSOC_f
zeta_2p_f = 9.746 * scale_2pSOC

H_i = H_i + Chop(zeta_3d_i * ldots_3d)


H_f = H_f + Chop(zeta_3d_f * ldots_3d + zeta_2p_f * ldots_2p)

-- Define the crystal field term.

Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
tenDq_3d = NewOperator('CF', NF, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{2, 0, -7}}
Ds_3d = NewOperator('CF', NF, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{4, 0, -21}}
Dt_3d = NewOperator('CF', NF, IndexUp_3d, IndexDn_3d, Akm)

H_i = H_i + Chop(tenDq_3d_i * tenDq_3d + Ds_3d_i * Ds_3d + Dt_3d_i * Dt_3d)

H_f = H_f + Chop(tenDq_3d_f * tenDq_3d + Ds_3d_f * Ds_3d + Dt_3d_f * Dt_3d)

Hamiltonian = H_i
XASHamiltonian = H_f
 
-- We saw in the previous example that NiO has a ground-state doublet with occupation 
-- t2g^6 eg^2 and S=1 (S^2=S(S+1)=2). The next state is 1.1 eV higher in energy and thus
-- unimportant for the ground-state upto temperatures of 10 000 Kelvin. We thus restrict 
-- the calculation to the lowest 3 eigenstates.
Npsi=3
-- in order to make sure we have a filling of 8
-- electrons we need to define some restrictions
-- We need to restrict the occupation of the Ni-2p shell to 6 for the ground state and for
-- the Ni 3d-shell to 8.
StartRestrictions = {NF, NB, {"111111 0000000000",6,6}, {"000000 1111111111",6,6}}
FinalRestrictions = {NF, NB, {'111111 0000000000', 6 - 1, 6 - 1},
                                         {'000000 1111111111', 6 + 1, 6 + 1}}
CalculationRestrictions = nil

 
-- And calculate the lowest 3 eigenfunctions
if initial_state > 1 then
  PsiList_i = Eigensystem(H_i, StartRestrictions, initial_state)

  Psi_i = PsiList_i[#PsiList_i]
else
  Psi_i = Eigensystem(H_i, StartRestrictions, 1)

end 
Psi_f = Eigensystem(H_f, FinalRestrictions, 1)

-- In order to get some information on these eigenstates it is good to plot expectation values
-- We first define a list of all the operators we would like to calculate the expectation value of
oppList={Hamiltonian, OppSsqr, OppLsqr, OppJsqr, OppSz, OppLz, Oppldots, OppF2, OppF4, OppNeg, OppNt2g};

PsiList = Eigensystem(H_i, StartRestrictions, NPsi_Initial)

 
-- next we loop over all operators and all states and print the expectation value
print(" <E>    <S^2>  <L^2>  <J^2>  <S_z>  <L_z>  <l.s>  <F[2]> <F[4]> <Neg>  <Nt2g>");
for i = 1,#PsiList do
  for j = 1,#oppList do
    expectationvalue = Chop(PsiList[i]*oppList[j]*PsiList[i])
    io.write(string.format("%8.3f ",Complex.Re(expectationvalue)))
  end
  io.write("\n")
end



 
-- calculating the spectra is simple and single line once all operators and wave-functions
-- are defined.
 
-- we here calculate the spectra for x,y,z polarized light and seperate the excitations into the t2g or eg sub-shell.
-- Then, we combine these and get the isotropic signal
 
-- The below comment shows which transition operators to use to also get the contributions from the 2p1/2 or 2p3/2 orbitals
--XASSpectra = CreateSpectra(XASHamiltonian, {TXASx,TXASxeg,TXASxt2g,TXASxj12,TXASxj32}, Psi_i, {{"Emin",-10}, {"Emax",20}, {"NE",3000}, {"Gamma",0.1}})

E1min_L3 = energy_start - E_2p
NE1_L3 = math.floor((energy_end - energy_start) / energy_step)
E1max_L3 = E1min_L3 + NE1_L3 * energy_step

E2min = loss_start
NE2 = math.floor((loss_end - loss_start) / loss_step)
E2max = E2min + NE2 * loss_step
  
-- XAS spectra
XAS_iso = CreateSpectra(H_f, {TXASx,TXASy,TXASz}, Psi_i,
	{{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}})
	
XAS_iso_t2g = CreateSpectra(H_f, {TXASxt2g,TXASyt2g,TXASzt2g}, Psi_i,
	{{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}})

XAS_iso_eg = CreateSpectra(H_f, {TXASxeg,TXASyeg,TXASzeg}, Psi_i,
	{{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}})

XAS_iso = Spectra.Sum(XAS_iso,{-1, -1, -1})
XAS_iso_t2g = Spectra.Sum(XAS_iso_t2g,{-1, -1, -1})
XAS_iso_eg = Spectra.Sum(XAS_iso_eg,{-1, -1, -1})
	
XAS_iso.Shift(E_2p)
XAS_iso_t2g.Shift(E_2p)
XAS_iso_eg.Shift(E_2p)

-- RIXS

RIXS = CreateResonantSpectra(H_f, H_i, {TXASx,TXASy,TXASz}, {T3d2px, T3d2py, T3d2pz},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})

RIXS_eg_eg = CreateResonantSpectra(H_f, H_i, {TXASxeg,TXASyeg,TXASzeg}, {T3d2pxeg, T3d2pyeg, T3d2pzeg},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})

RIXS_eg_t2g = CreateResonantSpectra(H_f, H_i, {TXASxeg,TXASyeg,TXASzeg}, {T3d2pxt2g, T3d2pyt2g, T3d2pzt2g},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})

RIXS_t2g_eg = CreateResonantSpectra(H_f, H_i, {TXASxt2g,TXASyt2g,TXASzt2g}, {T3d2pxeg, T3d2pyeg, T3d2pzeg},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})

RIXS_t2g_t2g = CreateResonantSpectra(H_f, H_i, {TXASxt2g,TXASyt2g,TXASzt2g}, {T3d2pxt2g, T3d2pyt2g, T3d2pzt2g},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})
		  
RIXS_eg_all = CreateResonantSpectra(H_f, H_i, {TXASxeg,TXASyeg,TXASzeg}, {T3d2px, T3d2py, T3d2pz},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})
		  
RIXS_t2g_all = CreateResonantSpectra(H_f, H_i, {TXASxt2g,TXASyt2g,TXASzt2g}, {T3d2px, T3d2py, T3d2pz},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})

RIXS_all_eg = CreateResonantSpectra(H_f, H_i, {TXASx,TXASy,TXASz}, {T3d2pxeg, T3d2pyeg, T3d2pzeg},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})
		  
RIXS_all_t2g = CreateResonantSpectra(H_f, H_i, {TXASx,TXASy,TXASz}, {T3d2pxt2g, T3d2pyt2g, T3d2pzt2g},
          Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
          {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2}})
		  

RIXSiso = 0
RIXSiso_eg_eg = 0
RIXSiso_eg_t2g = 0
RIXSiso_t2g_eg = 0
RIXSiso_t2g_t2g = 0
RIXSiso_eg_all = 0
RIXSiso_t2g_all = 0
RIXSiso_all_eg = 0
RIXSiso_all_t2g = 0
offset = 0
for i = 1, 3 * 3 do
	indices = {}
for j = 1, NE1_L3 + 1 do
	table.insert(indices, j + offset)
end
	RIXSiso = RIXSiso - Spectra.Element(RIXS, indices)
	RIXSiso_eg_eg = RIXSiso_eg_eg - Spectra.Element(RIXS_eg_eg, indices)
	RIXSiso_eg_t2g = RIXSiso_eg_t2g - Spectra.Element(RIXS_eg_t2g, indices)
	RIXSiso_t2g_eg = RIXSiso_t2g_eg - Spectra.Element(RIXS_t2g_eg, indices)
	RIXSiso_t2g_t2g = RIXSiso_t2g_t2g - Spectra.Element(RIXS_t2g_t2g, indices)
	RIXSiso_eg_all = RIXSiso_eg_all - Spectra.Element(RIXS_eg_all, indices)
	RIXSiso_t2g_all = RIXSiso_t2g_all - Spectra.Element(RIXS_t2g_all, indices)
	RIXSiso_all_eg = RIXSiso_all_eg - Spectra.Element(RIXS_all_eg, indices)
	RIXSiso_all_t2g = RIXSiso_all_t2g - Spectra.Element(RIXS_all_t2g, indices)
	offset = offset + NE1_L3 + 1
end
 
-- in order to plot the spectra we write them to file in ASCII format
-- note that the calculated object, i.e. <psi | T^dag 1/(w-H+IG/2) T | psi>
-- is complex. Minus the imaginary part is the absorption.

outname = name .. '_' .. tostring(math.floor(initial_state))

xas_iso_name = "XAS_iso" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
XAS_iso_t2g_name = "XAS_iso_t2g" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
XAS_iso_eg_name = "XAS_iso_eg" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'

RIXSiso_name = "RIXSiso" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_eg_eg_name = "RIXSiso_eg_eg" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_eg_t2g_name = "RIXSiso_eg_t2g" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_t2g_eg_name = "RIXSiso_t2g_eg" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_t2g_t2g_name = "RIXSiso_t2g_t2g" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_eg_all_name = "RIXSiso_eg_all" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_t2g_all_name = "RIXSiso_t2g_all" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_all_eg_name = "RIXSiso_all_eg" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'
RIXSiso_all_t2g_name = "RIXSiso_all_t2g" .. '_' ..tostring(math.floor(initial_state)) .. '.dat'

XAS_iso.Print({{"file",xas_iso_name}})
XAS_iso_t2g.Print({{"file",XAS_iso_t2g_name}})
XAS_iso_eg.Print({{"file",XAS_iso_eg_name}})

RIXSiso.Print({{"file",RIXSiso_name}})
RIXSiso_eg_eg.Print({{"file",RIXSiso_eg_eg_name}})
RIXSiso_eg_t2g.Print({{"file",RIXSiso_eg_t2g_name}})
RIXSiso_t2g_eg.Print({{"file",RIXSiso_t2g_eg_name}})
RIXSiso_t2g_t2g.Print({{"file",RIXSiso_t2g_t2g_name}})
RIXSiso_eg_all.Print({{"file",RIXSiso_eg_all_name}})
RIXSiso_t2g_all.Print({{"file",RIXSiso_t2g_all_name}})
RIXSiso_all_eg.Print({{"file",RIXSiso_all_eg_name}})
RIXSiso_all_t2g.Print({{"file",RIXSiso_all_t2g_name}})