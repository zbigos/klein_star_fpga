from typing import List

def generate_header(sym_name: str) -> List[str]:
    header: List[str] = []
    header.append(f"""(kicad_symbol_lib (version 20201005) (generator kicad_symbol_editor)""")
    header.append(f"""  (symbol "{sym_name}:{sym_name}" (in_bom yes) (on_board yes)""")
    header.append(f"""    (property "Reference" "U" (id 0) (at 0 2 0)""")
    header.append(f"""      (effects (font (size 1.27 1.27)))""")
    header.append(f"""    )""")
    header.append(f"""    (property "Value" "{sym_name}" (id 1) (at 0 5 0)""")
    header.append(f"""      (effects (font (size 1.27 1.27)))""")
    header.append(f"""    )""")
    header.append(f"""    (property "Footprint" "Package_BGA:Lattice_caBGA-381_17.0x17.0mm_Layout20x20_P0.8mm_Ball0.4mm_Pad0.4mm_NSMD" (id 2) (at 0 8 0)""")
    header.append(f"""      (effects (font (size 1.27 1.27)) hide)""")
    header.append(f"""    )""")
    header.append(f"""    (property "Datasheet" "" (id 3) (at 0 0 0)""")
    header.append(f"""      (effects (font (size 1.27 1.27)) hide)""")
    header.append(f"""    )""")
    return header

def generate_footer() -> List[str]:
    footer: List[str] = []
    footer.append(f"""  )""")
    footer.append(f""")""")
    return footer

def emit_dqgroup(repr) -> List[str]:
    dqgroup_f: List[str] = []
    powerpins = repr[None]
    del repr[None]
    print([str(pp) for pp in powerpins])

    offset = 5
    toffset = -10

    for dqoff, (dqname, dqpios) in enumerate(sorted(repr.items())):
        toffset = offset
        offset += 1
        for pioff, (pionum, piopins) in enumerate(sorted(dqpios.items())):
            piodump = [(p.pio_group, p) for p in piopins]
            for _, pin in sorted(piodump):
                dqgroup_f.append(f"""      (pin input line (at -5.08 {-offset * 2.54} 0) (length 5.08)""")
                dqgroup_f.append(f"""        (name "{pin.function}/{pin.dqs}/{pin.dual}" (effects (font (size 1.27 1.27))))""")
                dqgroup_f.append(f"""        (number "{pin.pin_designator}" (effects (font (size 1.27 1.27))))""")
                dqgroup_f.append(f"""      )""")
                offset += 1
            offset += 1
            dqgroup_f.append(f"""      (text "PIO: {pionum}" (at 3 {-(offset - 6) * 2.54} 0)""")
            dqgroup_f.append(f"""        (effects (font (size 0.8 0.8)))""")
            dqgroup_f.append(f"""      )""")

            dqgroup_f.append(f"""      (polyline""")
            dqgroup_f.append(f"""        (pts""")
            dqgroup_f.append(f"""          (xy 0 {-(offset - 1.5) * 2.54})""")
            dqgroup_f.append(f"""          (xy 32.5 {-(offset - 1.5) * 2.54})""")
            dqgroup_f.append(f"""          (xy 32.5 {-(offset - 5.5) * 2.54})""")
            dqgroup_f.append(f"""          (xy 0 {-(offset - 5.5) * 2.54})""")
            dqgroup_f.append(f"""        )""")
            dqgroup_f.append(f"""        (stroke (width 0.0006)) (fill (type none))""")
            dqgroup_f.append(f"""      )""")

        dqgroup_f.append(f"""      (text "DQgroup: {dqname}" (at 6.35 {-(toffset - 1) * 2.54} 0)""")
        dqgroup_f.append(f"""        (effects (font (size 0.8 0.8)))""")
        dqgroup_f.append(f"""      )""")

        offset += 1
        dqgroup_f.append(f"""      (polyline""")
        dqgroup_f.append(f"""        (pts""")
        dqgroup_f.append(f"""          (xy 0 {-(offset - 1.5) * 2.54})""")
        dqgroup_f.append(f"""          (xy 35.0 {-(offset - 1.5) * 2.54})""")
        dqgroup_f.append(f"""          (xy 35.0 {-(toffset - 0.5) * 2.54})""")
        dqgroup_f.append(f"""          (xy 0 {-(toffset - 0.5) * 2.54})""")
        dqgroup_f.append(f"""        )""")
        dqgroup_f.append(f"""        (stroke (width 0.0006)) (fill (type none))""")
        dqgroup_f.append(f"""      )""")
        offset += 1


    dqgroup_f.append(f"""      (rectangle (start 0 0) (end 45 {-offset * 2.54})""")
    dqgroup_f.append(f"""        (stroke (width 0.001)) (fill (type background))""")
    dqgroup_f.append(f"""      )""")
    voff = 15
    for pp in powerpins:
        dqgroup_f.append(f"""      (pin input line (at {voff * 2.54} 5.08 270) (length 5.08)""")
        dqgroup_f.append(f"""        (name "{pp.function}/{pp.dual}" (effects (font (size 1.27 1.27))))""")
        dqgroup_f.append(f"""        (number "{pp.pin_designator}" (effects (font (size 1.27 1.27))))""")
        dqgroup_f.append(f"""      )""")
        voff += 1

    return dqgroup_f

def emit_serdes(repr) -> List[str]:
    serdes_f: List[str] = []
    offset = 5
    pinset = [(f.function, f) for f in repr[None]]
    for _, pin in sorted(pinset):
        serdes_f.append(f"""      (pin input line (at -5.08 {-offset * 2.54} 0) (length 5.08)""")
        serdes_f.append(f"""        (name "{pin.function}/{pin.dual}" (effects (font (size 1.27 1.27))))""")
        serdes_f.append(f"""        (number "{pin.pin_designator}" (effects (font (size 1.27 1.27))))""")
        serdes_f.append(f"""      )""")
        offset += 1

    serdes_f.append(f"""      (rectangle (start 0 0) (end 45 {-offset * 2.54})""")
    serdes_f.append(f"""        (stroke (width 0.001)) (fill (type background))""")
    serdes_f.append(f"""      )""")

    return serdes_f

def emit_sparsegroup(repr) -> List[str]:
    sparsegroup_f: List[str] = []
    pinset = repr[None]

    powerpins = pinset[None]
    del pinset[None]
    offset = 5

    for pioff, (piok, pioset) in enumerate(sorted(pinset.items())):
        piodump = [(p.pio_group, p) for p in pioset]
        for _, pin in sorted(piodump):
            sparsegroup_f.append(f"""      (pin input line (at -5.08 {-offset * 2.54} 0) (length 5.08)""")
            sparsegroup_f.append(f"""        (name "{pin.function}/{pin.dual}" (effects (font (size 1.27 1.27))))""")
            sparsegroup_f.append(f"""        (number "{pin.pin_designator}" (effects (font (size 1.27 1.27))))""")
            sparsegroup_f.append(f"""      )""")
            offset += 1

        offset += 1
        sparsegroup_f.append(f"""      (text "PIO: {piok}" (at 3 {-(offset - 4) * 2.54} 0)""")
        sparsegroup_f.append(f"""        (effects (font (size 0.8 0.8)))""")
        sparsegroup_f.append(f"""      )""")

        sparsegroup_f.append(f"""      (polyline""")
        sparsegroup_f.append(f"""        (pts""")
        sparsegroup_f.append(f"""          (xy 0 {-(offset - 1.5) * 2.54})""")
        sparsegroup_f.append(f"""          (xy 20 {-(offset - 1.5) * 2.54})""")
        sparsegroup_f.append(f"""          (xy 20 {-(offset - 3.5) * 2.54})""")
        sparsegroup_f.append(f"""          (xy 0 {-(offset - 3.5) * 2.54})""")
        sparsegroup_f.append(f"""        )""")
        sparsegroup_f.append(f"""        (stroke (width 0.0006)) (fill (type none))""")
        sparsegroup_f.append(f"""      )""")

    sparsegroup_f.append(f"""      (rectangle (start 0 0) (end 45 {-offset * 2.54})""")
    sparsegroup_f.append(f"""        (stroke (width 0.001)) (fill (type background))""")
    sparsegroup_f.append(f"""      )""")

    voff = 15
    for pp in powerpins:
        sparsegroup_f.append(f"""      (pin input line (at {voff * 2.54} 5.08 270) (length 5.08)""")
        sparsegroup_f.append(f"""        (name "{pp.function}/{pp.dual}" (effects (font (size 1.27 1.27))))""")
        sparsegroup_f.append(f"""        (number "{pp.pin_designator}" (effects (font (size 1.27 1.27))))""")
        sparsegroup_f.append(f"""      )""")
        voff += 1

    return sparsegroup_f


def emit_power(repr) -> List[str]:
    pblok_f: List[str] = []
    offset = 3
    pinset = [(f.function, f.pin_designator, f) for f in repr[None]]
    lpin = pinset[0][2]

    for _, _, pin in sorted(pinset):
        if lpin.function != pin.function:
            offset += 2
        lpin = pin

        pblok_f.append(f"""      (pin input line (at -5.08 {-offset * 2.54} 0) (length 5.08)""")
        pblok_f.append(f"""        (name "{pin.function}/{pin.dual}" (effects (font (size 1.27 1.27))))""")
        pblok_f.append(f"""        (number "{pin.pin_designator}" (effects (font (size 1.27 1.27))))""")
        pblok_f.append(f"""      )""")
        offset += 1

    pblok_f.append(f"""      (rectangle (start 0 0) (end 45 {-offset * 2.54})""")
    pblok_f.append(f"""        (stroke (width 0.001)) (fill (type background))""")
    pblok_f.append(f"""      )""")

    return pblok_f


def generate_symbol(repr, sym_name: str, bank: str, bit: int) -> List[str]:
    print(f"======= symbol {bank}")
    symrepr: List[str] = []
    symrepr.append(f"""    (symbol "{sym_name}_{bit}_0" """)
    
    if bank == None:
        bank = "Power"
    
    if bank == 50:
        bank = "SERDES"

    if bank == 40:
        bank = "SWD"

    symrepr.append(f"""      (text "Bank: {bank}" (at 15 -5 0)""")
    symrepr.append(f"""        (effects (font (size 5 5)))""")
    symrepr.append(f"""      )""")
    
    if bank in [0, 1]:
        symrepr += emit_sparsegroup(repr)
    elif bank in [2, 3, 6, 7]:
        symrepr += emit_dqgroup(repr)
    elif bank in ["SERDES", "SWD"]:
        symrepr += emit_serdes(repr)
    elif bank in ["Power"]:
        symrepr += emit_power(repr)
    else:
        print(bank, repr.keys(), repr)

    symrepr.append(f"""    )""")
    return symrepr

def generate_thing(sym_name: str, repr) -> str:
    sym_repr = []
    sym_repr += generate_header(sym_name)
    for bit, bankname in enumerate(repr.keys()):
        sym_repr += generate_symbol(repr[bankname], sym_name, bankname, bit + 1)
    sym_repr += generate_footer()
    return "\n".join(sym_repr)