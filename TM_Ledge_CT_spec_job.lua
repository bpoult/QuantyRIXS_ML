-----
-- TM_Ledge_CT_spec_job.lua
-- Generic 2p->3d (L-edge) RIXS and XAS calculation for transition-metal ions
-- with charge transfer (LMCT and MLCT) using a 36-fermion Fock space:
--   2p (6) + 3d (10) + L1 occupied ligand (10) + L2 unoccupied ligand (10)
-- Isotropic XAS and RIXS spectra using Green's function approach.
-- D4h crystal field and Oh ligand field with LMCT and MLCT.
--
-- Atomic Slater integrals and SOC constants are read from the .inp_quanty file
-- (auto-populated by generate_inp_quanty_CT() via parse_rcn.py).
-- Separate scale factors are used for each Slater integral (consistent with
-- TM_Ledge_spec_job.lua).
--
-- Based on CT/greenMLCT_Co3d6_D4h_RCN_conf_job.lua (preserved for posterity).

---------------------------------------------------------
-- Helper functions
function Split(s, delimiter)
    result = {};
    for match in (s..delimiter):gmatch("(.-)"..delimiter) do
        table.insert(result, match);
    end
    return result;
end

-- Will search for filename passed in from Python for matching extensions, and return either filename or nil
function find_file_with_extension(extension)
    -- filename is passed in from Python as a global variable
    if target_file_quanty and target_file_quanty:match("%." .. extension .. "$") then
        return target_file_quanty
    elseif target_file_rixs and target_file_rixs:match("%." .. extension .. "$") then
      return target_file_rixs
    end
    return nil
end
---------------------------------------------------------
-- Input
config_name = find_file_with_extension("inp_quanty")
name,ext = config_name:match'([^.]*).(.*)'

print('Quanty configuration file ' .. config_name)
print(' ')
for line in io.lines(config_name) do
  if line ~= '' and string.sub(line,0,1) ~= '#' then
    local x = Split(line,' ')
    print(line)
    if x[1] == 'NPsi_Initial' then
      NPsi_Initial = tonumber(x[3])
    end
    if x[1] == 'NPsi_Final' then
      NPsi_Final = tonumber(x[3])
    end
    if x[1] == 'initial_state' then
      initial_state = tonumber(x[3])
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
    if x[1] == 'tenDq_L1_i' then
      tenDq_L1_i = tonumber(x[3])
    end
    if x[1] == 'tenDq_L1_f' then
      tenDq_L1_f = tonumber(x[3])
    end
    if x[1] == 'Delta_3d_L1_i' then
      Delta_3d_L1_i = tonumber(x[3])
    end
    if x[1] == 'Delta_3d_L1_f' then
      Delta_3d_L1_f = tonumber(x[3])
    end
    if x[1] == 'Veg_3d_L1_i' then
      Veg_3d_L1_i = tonumber(x[3])
    end
    if x[1] == 'Veg_3d_L1_f' then
      Veg_3d_L1_f = tonumber(x[3])
    end
    if x[1] == 'Vt2g_3d_L1_i' then
      Vt2g_3d_L1_i = tonumber(x[3])
    end
    if x[1] == 'Vt2g_3d_L1_f' then
      Vt2g_3d_L1_f = tonumber(x[3])
    end
    if x[1] == 'tenDq_L2_i' then
      tenDq_L2_i = tonumber(x[3])
    end
    if x[1] == 'tenDq_L2_f' then
      tenDq_L2_f = tonumber(x[3])
    end
    if x[1] == 'Delta_3d_L2_i' then
      Delta_3d_L2_i = tonumber(x[3])
    end
    if x[1] == 'Delta_3d_L2_f' then
      Delta_3d_L2_f = tonumber(x[3])
    end
    if x[1] == 'Veg_3d_L2_i' then
      Veg_3d_L2_i = tonumber(x[3])
    end
    if x[1] == 'Veg_3d_L2_f' then
      Veg_3d_L2_f = tonumber(x[3])
    end
    if x[1] == 'Vt2g_3d_L2_i' then
      Vt2g_3d_L2_i = tonumber(x[3])
    end
    if x[1] == 'Vt2g_3d_L2_f' then
      Vt2g_3d_L2_f = tonumber(x[3])
    end
    -- Atomic RCN parameters (auto-populated by generate_inp_quanty_CT())
    if x[1] == 'NE_3d' then
      NE_3d = tonumber(x[3])
    end
    if x[1] == 'F2_3d3d_i_rcn' then
      F2_3d3d_i_rcn = tonumber(x[3])
    end
    if x[1] == 'F4_3d3d_i_rcn' then
      F4_3d3d_i_rcn = tonumber(x[3])
    end
    if x[1] == 'zeta_3d_i_rcn' then
      zeta_3d_i_rcn = tonumber(x[3])
    end
    if x[1] == 'F2_3d3d_f_rcn' then
      F2_3d3d_f_rcn = tonumber(x[3])
    end
    if x[1] == 'F4_3d3d_f_rcn' then
      F4_3d3d_f_rcn = tonumber(x[3])
    end
    if x[1] == 'F2_2p3d_rcn' then
      F2_2p3d_rcn = tonumber(x[3])
    end
    if x[1] == 'G1_2p3d_rcn' then
      G1_2p3d_rcn = tonumber(x[3])
    end
    if x[1] == 'G3_2p3d_rcn' then
      G3_2p3d_rcn = tonumber(x[3])
    end
    if x[1] == 'zeta_3d_f_rcn' then
      zeta_3d_f_rcn = tonumber(x[3])
    end
    if x[1] == 'zeta_2p_rcn' then
      zeta_2p_rcn = tonumber(x[3])
    end
  end
end
print(' ')

spec_config_name = find_file_with_extension("inp_rixs")
name,ext = spec_config_name:match'([^.]*).(.*)'

print('Spectra configuration file ' .. spec_config_name)
print(' ')
for line in io.lines(spec_config_name) do
  if line ~= '' and string.sub(line,0,1) ~= '#' then
    local x = Split(line,' ')
    print(line)
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
NFermions = 36

NE_2p = 6
-- NE_3d is read from .inp_quanty (set by generate_inp_quanty_CT() via parse_rcn.py)
NE_L1 = 10
NE_L2 = 0

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_3d = {6, 8, 10, 12, 14}
IndexUp_3d = {7, 9, 11, 13, 15}
IndexDn_L1 = {16, 18, 20, 22, 24}
IndexUp_L1 = {17, 19, 21, 23, 25}
IndexDn_L2 = {26, 28, 30, 32, 34}
IndexUp_L2 = {27, 29, 31, 33, 35}


-- Define the atomic term.
N_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

F0_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
F2_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
G1_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
G3_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

-- Slater integrals: RCN atomic values (from .inp_quanty) scaled by user-supplied factors
F2_3d_3d_i = F2_3d3d_i_rcn * scalef2_3d3d_i
F4_3d_3d_i = F4_3d3d_i_rcn * scalef4_3d3d_i
F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

F2_3d_3d_f = F2_3d3d_f_rcn * scalef2_3d3d_f
F4_3d_3d_f = F4_3d3d_f_rcn * scalef4_3d3d_f
F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
F2_2p_3d_f = F2_2p3d_rcn * scalef2_2p3d
G1_2p_3d_f = G1_2p3d_rcn * scaleg
G3_2p_3d_f = G3_2p3d_rcn * scaleg
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

ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

-- SOC: RCN atomic values (from .inp_quanty) scaled by user-supplied factors
zeta_3d_i = zeta_3d_i_rcn * scale_3dSOC_i

zeta_3d_f = zeta_3d_f_rcn * scale_3dSOC_f
zeta_2p_f = zeta_2p_rcn   * scale_2pSOC

H_i = H_i + Chop(zeta_3d_i * ldots_3d)

H_f = H_f + Chop(zeta_3d_f * ldots_3d + zeta_2p_f * ldots_2p)

-- Define the crystal field term.

Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{2, 0, -7}}
Ds_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)
Akm = {{4, 0, -21}}
Dt_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)

H_i = H_i + Chop(tenDq_3d_i * tenDq_3d + Ds_3d_i * Ds_3d + Dt_3d_i * Dt_3d)

H_f = H_f + Chop(tenDq_3d_f * tenDq_3d + Ds_3d_f * Ds_3d + Dt_3d_f * Dt_3d)

-- Define the 3d-ligands interaction energies

e_3d_i = (10 * Delta_3d_L1_i - NE_3d * (19 + NE_3d) * U_3d_3d_i/2) / (10 + NE_3d)
e_L1_i = NE_3d * (-1*Delta_3d_L1_i + (1 + NE_3d) * U_3d_3d_i/2) / (10 + NE_3d)
e_L2_i = (10 * Delta_3d_L1_i + (NE_3d + 10) * Delta_3d_L2_i + (NE_3d^2 - NE_3d - 20) * U_3d_3d_i / 2) / (10 + NE_3d)

e_2p_f = (10 * Delta_3d_L1_f + (1 + NE_3d) * (NE_3d * U_3d_3d_f / 2 - (10 + NE_3d) * U_2p_3d_f)) / (16 + NE_3d)
e_3d_f = (10 * Delta_3d_L1_f - NE_3d * (31 + NE_3d) * U_3d_3d_f / 2 - 90 * U_2p_3d_f) / (16 + NE_3d)
e_L1_f = ((1 + NE_3d) * (NE_3d * U_3d_3d_f / 2 + 6 * U_2p_3d_f) - (6 + NE_3d) * Delta_3d_L1_f) / (16 + NE_3d)
e_L2_f = (10 * Delta_3d_L1_f + (NE_3d + 16) * Delta_3d_L2_f + (NE_3d^2 - NE_3d -32) * U_3d_3d_f/2 + (6 * NE_3d + 6) * U_2p_3d_f) / (16 + NE_3d)

print(' ')
print('Orbital energies without core-orbitals:')
print(string.format('3d: %6.3f', e_3d_i))
print(string.format('L1: %6.3f', e_L1_i))
print(string.format('L2: %6.3f', e_L2_i))
print('Orbital energies with core-orbitals:')
print(string.format('2p: %6.3f', e_2p_f))
print(string.format('3d: %6.3f', e_3d_f))
print(string.format('L1: %5.3f', e_L1_f))
print(string.format('L2: %6.3f', e_L2_f))
print(' ')


-- LMCT
N_L1 = NewOperator('Number', NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
  + NewOperator('Number', NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

H_i = H_i + Chop(
  e_3d_i * N_3d +
  e_L1_i * N_L1)

H_f = H_f + Chop(
  e_3d_f * N_3d +
  e_2p_f * N_2p +
  e_L1_f * N_L1)

tenDq_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

Veg_3d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {1, 0}))
  + NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 2, {1, 0}))

Vt2g_3d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0, 1}))
  + NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 2, {0, 1}))

H_i = H_i + Chop(
  tenDq_L1_i * tenDq_L1 +
  Veg_3d_L1_i * Veg_3d_L1 +
  Vt2g_3d_L1_i * Vt2g_3d_L1)

H_f = H_f + Chop(
  tenDq_L1_f * tenDq_L1 +
  Veg_3d_L1_f * Veg_3d_L1 +
  Vt2g_3d_L1_f * Vt2g_3d_L1)

-- MLCT
N_L2 = NewOperator('Number', NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
  + NewOperator('Number', NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

H_i = H_i + Chop(
  e_L2_i * N_L2)

H_f = H_f + Chop(
  e_L2_f * N_L2)

tenDq_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

Veg_3d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {1, 0}))
  + NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Oh', 2, {1, 0}))

Vt2g_3d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0, 1}))
  + NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Oh', 2, {0, 1}))

H_i = H_i + Chop(
  tenDq_L2_i * tenDq_L2 +
  Veg_3d_L2_i * Veg_3d_L2 +
  Vt2g_3d_L2_i * Vt2g_3d_L2)

H_f = H_f + Chop(
  tenDq_L2_f * tenDq_L2 +
  Veg_3d_L2_f * Veg_3d_L2 +
  Vt2g_3d_L2_f * Vt2g_3d_L2)

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
Tx_2p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm_x)
Ty_2p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm_y)
Tz_2p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, Akm_z)
Tx_3d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm_x)
Ty_3d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm_y)
Tz_3d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, Akm_z)

-- Define the restrictions and set the number of initial states.

InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000 0000000000', NE_2p, NE_2p},
                                           {'000000 1111111111 0000000000 0000000000', NE_3d, NE_3d},
                                           {'000000 0000000000 1111111111 0000000000', NE_L1, NE_L1},
                                           {'000000 0000000000 0000000000 1111111111', NE_L2, NE_L2}}

FinalRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000 0000000000', NE_2p - 1, NE_2p - 1},
                                         {'000000 1111111111 0000000000 0000000000', NE_3d + 1, NE_3d + 1},
                                         {'000000 0000000000 1111111111 0000000000', NE_L1, NE_L1},
                                         {'000000 0000000000 0000000000 1111111111', NE_L2, NE_L2}}

CalculationRestrictions = {NFermions, NBosons, {'000000 0000000000 1111111111 0000000000', NE_L1 - 1, NE_L1},
                                               {'000000 0000000000 0000000000 1111111111', NE_L2, NE_L2 + 1}}

-- Calculate the initial eigenstate

if initial_state > 1 then
  PsiList_i = Eigensystem(H_i, InitialRestrictions, initial_state, {{'restrictions', CalculationRestrictions}})

  Psi_i = PsiList_i[#PsiList_i]
else
  Psi_i = Eigensystem(H_i, InitialRestrictions, 1, {{'restrictions', CalculationRestrictions}})

end
Psi_f = Eigensystem(H_f, FinalRestrictions, 1, {{'restrictions', CalculationRestrictions}})

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
  XAS_L3 = CreateSpectra(H_f, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, Psi_i,
        {{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}, {'restrictions', CalculationRestrictions}})
  XAS_L2 = CreateSpectra(H_f, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, Psi_i,
        {{'Emin', E1min_L2}, {'Emax', E1max_L2}, {'NE', NE1_L2}, {'Gamma', Gamma1_L2}, {'restrictions', CalculationRestrictions}})
  --
  XASiso_L3 = Spectra.Sum(XAS_L3,{-1, -1, -1})
  XASiso_L2 = Spectra.Sum(XAS_L2,{-1, -1, -1})
  XASiso_L3.Shift(E_2p)
  XASiso_L2.Shift(E_2p)

  XASiso_L3.Print({{"file",filename1a}})
  print('Saved file ' .. filename1a)
  XASiso_L2.Print({{"file",filename1b}})
  print('Saved file ' .. filename1b)

  -- RIXS spectra
  -- RIXS_L3 = CreateResonantSpectra(H_f, H_i, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, {Tx_3d_2p, Ty_3d_2p, Tz_3d_2p},
  --         Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
  --         {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2},
  --         {'restrictions1', CalculationRestrictions}, {'restrictions2', CalculationRestrictions}})
  -- RIXS_L2 = CreateResonantSpectra(H_f, H_i, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, {Tx_3d_2p, Ty_3d_2p, Tz_3d_2p},
  --         Psi_i, {{'Emin1', E1min_L2}, {'Emax1', E1max_L2}, {'NE1', NE1_L2}, {'Gamma1', Gamma1_L2},
  --         {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2},
  --         {'restrictions1', CalculationRestrictions}, {'restrictions2', CalculationRestrictions}})
  -- --
  -- RIXSiso_L3 = 0
  -- offset = 0
  -- for i = 1, 3 * 3 do
  --   indices = {}
  --   for j = 1, NE1_L3 + 1 do
  --     table.insert(indices, j + offset)
  --   end
  --   RIXSiso_L3 = RIXSiso_L3 - Spectra.Element(RIXS_L3, indices)
  --   offset = offset + NE1_L3 + 1
  -- end
  -- --
  -- RIXSiso_L2 = 0
  -- offset = 0
  -- for i = 1, 3 * 3 do
  --   indices = {}
  --   for j = 1, NE1_L2 + 1 do
  --     table.insert(indices, j + offset)
  --   end
  --   RIXSiso_L2 = RIXSiso_L2 - Spectra.Element(RIXS_L2, indices)
  --   offset = offset + NE1_L2 + 1
  -- end

  -- RIXSiso_L3.Print({{'file', filename2a}})
  -- print('Saved file ' .. filename2a)
  -- RIXSiso_L2.Print({{'file', filename2b}})
  -- print('Saved file ' .. filename2b)

else
  E1min_L3 = energy_start - E_2p
  NE1_L3 = math.floor((energy_end - energy_start) / energy_step)
  E1max_L3 = E1min_L3 + NE1_L3 * energy_step

  E2min = loss_start
  NE2 = math.floor((loss_end - loss_start) / loss_step)
  E2max = E2min + NE2 * loss_step

  -- XAS spectra
  XAS_L3 = CreateSpectra(H_f, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, Psi_i,
        {{'Emin', E1min_L3}, {'Emax', E1max_L3}, {'NE', NE1_L3}, {'Gamma', Gamma1_L3}, {'restrictions', CalculationRestrictions}})
  --
  XASiso_L3 = Spectra.Sum(XAS_L3,{-1, -1, -1})
  XASiso_L3.Shift(E_2p)

  XASiso_L3.Print({{"file",filename1a}})
  print('Saved file ' .. filename1a)

  -- RIXS spectra
--   RIXS_L3 = CreateResonantSpectra(H_f, H_i, {Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}, {Tx_3d_2p, Ty_3d_2p, Tz_3d_2p},
--           Psi_i, {{'Emin1', E1min_L3}, {'Emax1', E1max_L3}, {'NE1', NE1_L3}, {'Gamma1', Gamma1_L3},
--           {'Emin2', E2min}, {'Emax2', E2max}, {'NE2', NE2}, {'Gamma2', Gamma2},
--           {'restrictions1', CalculationRestrictions}, {'restrictions2', CalculationRestrictions}})
--   --

--   RIXSiso_L3 = 0
--   offset = 0
--   for i = 1, 3 * 3 do
--     indices = {}
--     for j = 1, NE1_L3 + 1 do
--       table.insert(indices, j + offset)
--     end
--     RIXSiso_L3 = RIXSiso_L3 - Spectra.Element(RIXS_L3, indices)
--     offset = offset + NE1_L3 + 1
--   end

--   RIXSiso_L3.Print({{'file', filename2a}})
--   print('Saved file ' .. filename2a)
end

print('Finished.')
