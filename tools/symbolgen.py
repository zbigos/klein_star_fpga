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
    header.append(f"""    (property "Footprint" "Package_BGA:BGA-96_9.0x13.0mm_Layout2x3x16_P0.8mm" (id 2) (at 0 8 0)""")
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

def emit_sparsegroup(repr) -> List[str]:
    sparsegroup_f: List[str] = []
    pinset = repr[None]

    powerpins = pinset[None]
    del pinset[None]

    print([str(pp) for pp in powerpins])

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
        sparsegroup_f.append(f"""        (name "{pp.function}/{pin.dual}" (effects (font (size 1.27 1.27))))""")
        sparsegroup_f.append(f"""        (number "{pp.pin_designator}" (effects (font (size 1.27 1.27))))""")
        sparsegroup_f.append(f"""      )""")
        voff += 1

    return sparsegroup_f

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

    symrepr.append(f"""    )""")
    return symrepr

def generate_thing(sym_name: str, repr) -> str:
    sym_repr = []
    sym_repr += generate_header(sym_name)
    for bit, bankname in enumerate(repr.keys()):
        sym_repr += generate_symbol(repr[bankname], sym_name, bankname, bit + 1)
    sym_repr += generate_footer()
    return "\n".join(sym_repr)