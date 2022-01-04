from classes import Pin, FPGA
from symbolgen import generate_thing

pins = []
with open('pinout.csv', 'r') as f:
    data = f.read().split('\n')
    for l in data[5:-1]:
        pad, pin_ball, bank, dual, diff, hi_speed, dqs, pp, _ = l.split(',')
        try:
            if pp != '-':
                pins.append(
                    Pin(
                        pad=int(pad),
                        dual=dual,
                        pin_function=pin_ball,
                        pin_designator=pp,
                        bank=bank,
                        dqs=dqs
                    )
                )
        except Exception as e:
            print(repr(e))
            print(l)
            exit(1)


fpga = FPGA()
for pin in pins:
    fpga.add_pin(pin)

fpga.info()
group_dump = fpga.dump_groups()
for k, v in group_dump.items():
    group_dump[k] = fpga.dump_dqs(v)

for k, v in group_dump.items():
    for gname, gcontents in group_dump[k].items():
        succ, nd = fpga.dump_pio(gcontents)
        if succ:
            group_dump[k][gname] = nd

# for bank, v in group_dump.items():
#    print(f"{bank}:")
#    for dqs, pins in v.items():
#        print(f"    {dqs} {[p.pin_designator for p in pins]}")

fpga.treeify(group_dump)
symv = generate_thing('ECP5UM25', group_dump)
with open('ECP5UM25.kicad_sym', 'w') as f:
    f.write(symv)
