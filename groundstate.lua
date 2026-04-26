-----
-- 02.02.2026
-- 2p3d calculation of Co3+ 3d6 ion
-- Isotropic XAS and RIXS spectra using Greens function 
-- D4h crystal field and Oh ligand field with LMCT and MLCT

---------------------------------------------------------
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

-- End of Input
---------------------------------------------------------
-- Initialize the Hamiltonians
H_i = 0
H_f = 0

-- Define the number of electrons, shells, etc.
NBosons = 0
NFermions = 10

NE_3d = 6

IndexDn_3d = {0,2,4,6,8}
IndexUp_3d = {1,3,5,7,9}


-- Define some operators:

OppSx   =NewOperator("Sx"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppSy   =NewOperator("Sy"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppSz   =NewOperator("Sz"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppSsqr =NewOperator("Ssqr" ,NFermions, IndexUp_3d, IndexDn_3d)
OppSplus=NewOperator("Splus",NFermions, IndexUp_3d, IndexDn_3d)
OppSmin =NewOperator("Smin" ,NFermions, IndexUp_3d, IndexDn_3d)
 
OppLx   =NewOperator("Lx"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppLy   =NewOperator("Ly"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppLz   =NewOperator("Lz"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppLsqr =NewOperator("Lsqr" ,NFermions, IndexUp_3d, IndexDn_3d)
OppLplus=NewOperator("Lplus",NFermions, IndexUp_3d, IndexDn_3d)
OppLmin =NewOperator("Lmin" ,NFermions, IndexUp_3d, IndexDn_3d)
 
OppJx   =NewOperator("Jx"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppJy   =NewOperator("Jy"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppJz   =NewOperator("Jz"   ,NFermions, IndexUp_3d, IndexDn_3d)
OppJsqr =NewOperator("Jsqr" ,NFermions, IndexUp_3d, IndexDn_3d)
OppJplus=NewOperator("Jplus",NFermions, IndexUp_3d, IndexDn_3d)
OppJmin =NewOperator("Jmin" ,NFermions, IndexUp_3d, IndexDn_3d)


Sx_3d = NewOperator("Sx", NFermions, IndexUp_3d, IndexDn_3d)
Sy_3d = NewOperator("Sy", NFermions, IndexUp_3d, IndexDn_3d)
Sz_3d = NewOperator("Sz", NFermions, IndexUp_3d, IndexDn_3d)
Ssqr_3d = NewOperator("Ssqr", NFermions, IndexUp_3d, IndexDn_3d)
Splus_3d = NewOperator("Splus", NFermions, IndexUp_3d, IndexDn_3d)
Smin_3d = NewOperator("Smin", NFermions, IndexUp_3d, IndexDn_3d)

Lx_3d = NewOperator("Lx", NFermions, IndexUp_3d, IndexDn_3d)
Ly_3d = NewOperator("Ly", NFermions, IndexUp_3d, IndexDn_3d)
Lz_3d = NewOperator("Lz", NFermions, IndexUp_3d, IndexDn_3d)
Lsqr_3d = NewOperator("Lsqr", NFermions, IndexUp_3d, IndexDn_3d)
Lplus_3d = NewOperator("Lplus", NFermions, IndexUp_3d, IndexDn_3d)
Lmin_3d = NewOperator("Lmin", NFermions, IndexUp_3d, IndexDn_3d)

Jx_3d = NewOperator("Jx", NFermions, IndexUp_3d, IndexDn_3d)
Jy_3d = NewOperator("Jy", NFermions, IndexUp_3d, IndexDn_3d)
Jz_3d = NewOperator("Jz", NFermions, IndexUp_3d, IndexDn_3d)
Jsqr_3d = NewOperator("Jsqr", NFermions, IndexUp_3d, IndexDn_3d)
Jplus_3d = NewOperator("Jplus", NFermions, IndexUp_3d, IndexDn_3d)
Jmin_3d = NewOperator("Jmin", NFermions, IndexUp_3d, IndexDn_3d)

Tx_3d = NewOperator("Tx", NFermions, IndexUp_3d, IndexDn_3d)
Ty_3d = NewOperator("Ty", NFermions, IndexUp_3d, IndexDn_3d)
Tz_3d = NewOperator("Tz", NFermions, IndexUp_3d, IndexDn_3d)

Sx = Sx_3d
Sy = Sy_3d
Sz = Sz_3d

Lx = Lx_3d
Ly = Ly_3d
Lz = Lz_3d

Jx = Jx_3d
Jy = Jy_3d
Jz = Jz_3d

Tx = Tx_3d
Ty = Ty_3d
Tz = Tz_3d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz
 

-- Define the atomic term.
N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})


F2_3d_3d_i = 12.663 * scalef2_3d3d_i
F4_3d_3d_i = 7.917 * scalef4_3d3d_i
F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i


H_i = H_i + Chop(
  F0_3d_3d_i * F0_3d_3d
  + F2_3d_3d_i * F2_3d_3d
  + F4_3d_3d_i * F4_3d_3d)


ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

zeta_3d_i = 0.0739 * scale_3dSOC_i

H_i = H_i + Chop(zeta_3d_i * ldots_3d)


-- Define the crystal field term.
Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{2, 0, -7}}
Ds_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{4, 0, -21}}
Dt_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)

H_i = H_i + Chop(tenDq_3d_i * tenDq_3d + Ds_3d_i * Ds_3d + Dt_3d_i * Dt_3d)

Dq_3d_i = tenDq_3d_i/10

local orbitals = {
    {irrep = "a1g", energy = 6 * Dq_3d_i - 2 * Ds_3d_i - 6 * Dt_3d_i},
    {irrep = "b1g", energy = 6 * Dq_3d_i + 2 * Ds_3d_i - Dt_3d_i},
    {irrep = "b2g", energy = -4 * Dq_3d_i + 2 * Ds_3d_i - Dt_3d_i},
    {irrep = "eg ", energy = -4 * Dq_3d_i - Ds_3d_i + 4 * Dt_3d_i}
}

-- Sort by energy (ascending order)
table.sort(orbitals, function(a, b) return a.energy > b.energy end)

-- Print sorted results
io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
io.write("================\n")
io.write("Irrep.         E\n")
io.write("================\n")
for i = 1, #orbitals do
    io.write(string.format("%s     %8.3f\n", orbitals[i].irrep, orbitals[i].energy))
end
io.write("================\n")
io.write("\n")

if (Ds_3d_i and Dt_3d_i) ~= 0 then

	Akm = PotentialExpandedOnClm("D4h",2,{1,0,0,0});
	OppNa1g = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);
	--Akm = PotentialExpandedOnClm("Oh",2,{0,1});
	Akm = PotentialExpandedOnClm("D4h",2,{0,1,0,0});
	OppNb1g = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);
	Akm = PotentialExpandedOnClm("D4h",2,{0,0,1,0});
	OppNb2g = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);
	Akm = PotentialExpandedOnClm("D4h",2,{0,0,0,1});
	OppNeg = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);

	oppList = {Ssqr, Lsqr, Jsqr,ldots_3d,OppNb2g,OppNeg,OppNb1g,OppNa1g}

else
	Akm = PotentialExpandedOnClm("Oh",2,{1,0});
	OppNeg = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);
	Akm = PotentialExpandedOnClm("Oh",2,{0,1});
	OppNt2g = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm);

	oppList = {Ssqr, Lsqr, Jsqr,ldots_3d,OppNt2g,OppNeg}

end

-- Define the restrictions and set the number of initial states.

InitialRestrictions = {NFermions, NBosons, {'1111111111', NE_3d, NE_3d}}

CalculationRestrictions = nil



psiList = Eigensystem(H_i, InitialRestrictions, NPsi_Initial);
if (Ds_3d_i and Dt_3d_i) ~= 0 then
	print("State    <E>      <S^2>     <L^2>     <J^2>     <l.s>     <Nb2g>    <Neg>     <Nb1g>    <Na1g>");
else
	print("State    <E>      <S^2>     <L^2>     <J^2>     <l.s>     <Nt2g>    <Neg>");
end

for i = 1,#psiList do
  io.write(string.format("%3d:   ", i))  -- Print i with width of 3 at the beginning
  E0 = psiList[1]*H_i*psiList[1]
  E = psiList[i]*H_i*psiList[i]
  E = E - E0
  --E = string(E)
  io.write(string.format("%6.3f    ",(E)))

  for j = 1,#oppList do
    expectationvalue = Chop(psiList[i]*oppList[j]*psiList[i])
    io.write(string.format("%6.3f    ",expectationvalue))
  end
  io.write("\n")
end
print('Finished.')
