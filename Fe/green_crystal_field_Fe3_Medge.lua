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
NFermions = 16

NE_3p = 6
NE_3d = 5

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_3d = {6, 8, 10, 12, 14}
IndexUp_3d = {7, 9, 11, 13, 15}


-- Define the atomic term.
N_3p = NewOperator("Number", NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_3d = NewOperator("Number", NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

F0_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
F2_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
G1_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
G3_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

F2_3d_3d_i = 12.043 * scalef2_3d3d_i
F4_3d_3d_i = 7.535 * scalef4_3d3d_i
F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

F2_3d_3d_f = 12.091 * scalef2_3d3d_f
F4_3d_3d_f = 7.565 * scalef4_3d3d_f
F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
F2_3p_3d_f = 13.050 * scalef2_2p3d
G1_3p_3d_f = 16.176 * scaleg
G3_3p_3d_f = 9.854 * scaleg
F0_3p_3d_f = U_2p_3d_f + 1 / 15 * G1_3p_3d_f + 3 / 70 * G3_3p_3d_f

H_i = H_i + Chop(
  F0_3d_3d_i * F0_3d_3d
  + F2_3d_3d_i * F2_3d_3d
  + F4_3d_3d_i * F4_3d_3d)

H_f = H_f + Chop(
  F0_3d_3d_f * F0_3d_3d
  + F2_3d_3d_f * F2_3d_3d
  + F4_3d_3d_f * F4_3d_3d
  + F0_3p_3d_f * F0_3p_3d
  + F2_3p_3d_f * F2_3p_3d
  + G1_3p_3d_f * G1_3p_3d
  + G3_3p_3d_f * G3_3p_3d)

ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

ldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

zeta_3d_i = 0.059 * scale_3dSOC_i

zeta_3d_f = 0.059 * scale_3dSOC_f
zeta_3p_f = 0.969 * scale_2pSOC

H_i = H_i + Chop(zeta_3d_i * ldots_3d)

H_f = H_f + Chop(zeta_3d_f * ldots_3d + zeta_3p_f * ldots_3p)

-- Define the crystal field term.

Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{2, 0, -7}}
Ds_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{4, 0, -21}}
Dt_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)

H_i = H_i + Chop(tenDq_3d_i * tenDq_3d + Ds_3d_i * Ds_3d + Dt_3d_i * Dt_3d)

H_f = H_f + Chop(tenDq_3d_f * tenDq_3d + Ds_3d_f * Ds_3d + Dt_3d_f * Dt_3d)


-- Define the transition operators.
-- x polarized light is defined as x = Cos[phi]Sin[theta] = sqrt(1/2) ( C_1^{(-1)} - C_1^{(1)})
-- y polarized light is defined as y = Sin[phi]Sin[theta] = sqrt(1/2) I ( C_1^{(-1)} + C_1^{(1)})
-- z polarized light is defined as z = Cos[theta] = C_1^{(0)}

Akm_x = {{1, -1,1/math.sqrt(2)},
        {1,  0, 0},
        {1,  1,-1/math.sqrt(2)}}
Akm_y = {{1, -1,I * 1/math.sqrt(2)},
        {1,  0, 0},
        {1,  1,I * 1/math.sqrt(2)}}
Akm_z = {{1, -1,0},
        {1,  0, 1},
        {1,  1, 0}}
Tx_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, Akm_x)
Ty_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, Akm_y)
Tz_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, Akm_z)
Tx_3d_2p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, Akm_x)
Ty_3d_2p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, Akm_y)
Tz_3d_2p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, Akm_z)

-- Define the restrictions and set the number of initial states.

InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NE_3p, NE_3p},
                                           {'000000 1111111111', NE_3d, NE_3d}}

FinalRestrictions = {NFermions, NBosons, {'111111 0000000000', NE_3p - 1, NE_3p - 1},
                                         {'000000 1111111111', NE_3d + 1, NE_3d + 1}}

CalculationRestrictions = nil


-- Calculate the initial eigenstate

if initial_state > 1 then
  PsiList_i = Eigensystem(H_i, InitialRestrictions, initial_state)

  Psi_i = PsiList_i[#PsiList_i]
else
  Psi_i = Eigensystem(H_i, InitialRestrictions, 1)

end
Psi_f = Eigensystem(H_f, FinalRestrictions, 1)

-- Calculate the spectra

E_i = Psi_i * H_i * Psi_i
E_f = Psi_f * H_f * Psi_f
print(' ')
print(string.format('Lowest energy valence state = %4.3f eV', E_i))
print(string.format('Lowest energy core state    = %4.3f eV', E_f))
print(string.format('Difference with 2p shift    = %4.3f eV', E_f - E_i + E_2p))
print(' ')

outname = name .. '_' .. tostring(math.floor(initial_state))
filename1a = 'XASisoL3_' .. outname .. '.txt'
filename1b = 'XASisoL2_' .. outname .. '.txt'
filename2a = 'RIXSisoL3_' .. outname .. '.txt'
filename2b = 'RIXSisoL2_' .. outname .. '.txt'

if energy_end > L3_L2_split then
  E1min_L3 = energy_start - E_2p
  NE1_L3 = math.floor((L3_L2_split - energy_start) / energy_step)
  E1max_L3 = E1min_L3 + NE1_L3 * energy_step

  E1min_L2 = energy_start - E_2p + (NE1_L3 + 1) * energy_step
  NE1_L2 = math.floor((energy_end - E_2p - E1min_L2) / energy_step)
  E1max_L2 = E1min_L2 + NE1_L2 * energy_step

  E2min = loss_start
  NE2 = math.floor((loss_end - loss_start) / loss_step)
  E2max = E2min + NE2 * loss_step

  -- XAS spectra
  XAS_L3 = CreateSpectra(H_f, {Tx_3p_3d, Ty_3p_3d, Tz_3p_3d}, Psi_i,
        {{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}})
  XAS_L2 = CreateSpectra(H_f, {Tx_3p_3d, Ty_3p_3d, Tz_3p_3d}, Psi_i,
        {{'Emin', E1min_L2}, {'Emax', E1max_L2}, {'NE', NE1_L2}, {'Gamma', Gamma1_L2}})
  --
  XASiso_L3 = Spectra.Sum(XAS_L3,{-1, -1, -1})
  XASiso_L2 = Spectra.Sum(XAS_L2,{-1, -1, -1})
  XASiso_L3.Shift(E_2p)
  XASiso_L2.Shift(E_2p)
  
  XASiso_L3.Broaden(0.2, {{50,0.1}, {54.5,1.5},{76,1.5}})

  XASiso_L3.Print({{"file",filename1a}})
  print('Saved file ' .. filename1a)
  XASiso_L2.Print({{"file",filename1b}})
  print('Saved file ' .. filename1b)

end

print('Finished.')
