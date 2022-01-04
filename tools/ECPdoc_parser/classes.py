from typing import Any, List, Dict, Tuple, Set, Optional, List
import json
import sys
import os
import copy
import logging
import matplotlib
import matplotlib.pyplot as plt
import uuid
import matplotlib.patches as patches
from treelib import Node, Tree

class Pin:
    """
        dataclass for storing info about fpga pin.
    """

    def __init__(self, pad: int, dual: str, pin_function: str, pin_designator: str, bank: int, dqs: str) -> None:
        self.function: str = pin_function
        self.pad: int = pad
        self.dual: str = dual

        if dqs == '-':
            self.dqs = None
        else:
            self.dqs: str = dqs

        self.row = pin_designator[0]
        if len(pin_designator) == 2:
            self.col = pin_designator[1]
        else:
            self.col = pin_designator[1] + pin_designator[2]

        try:
            self.bank: int = int(bank)
        except ValueError:
            self.bank = None

        try:
            self.pio_side: Optional[str] = pin_function[1]
            self.pio_group: Optional[str] = pin_function[-1]
            self.pio_num: Optional[int] = int(pin_function[2:-1])
        except ValueError:
            self.pio_side = None
            self.pio_group = None
            self.pio_num = None


    def __str__(self) -> str:
        return f'{self.row}{self.col}: ({self.function}) (pio: {self.pio_side} {self.pio_num} {self.pio_group}) , dqs: {self.dqs})'

    @property
    def pin_designator(self) -> str:
        return f'{self.row}{self.col}'

class FPGA:
    """
        dataclass for storing info about FPGA.
    """

    def __init__(self) -> None:
        self.pins: Dict[Tuple(str, int), Pin] = {}
        self.v_pins = 0
        self.h_pins = 0

    def add_pin(self, pin: Pin) -> None:
        if pin.pin_designator in self.pins.keys():
            logging.critical(f'you are trying to add {pin.pin_designator} but there already exists one!')
            logging.critical(f'current {str(self.pins[pin.pin_designator])}')
            logging.critical(f'incoming {str(pin)}')
            logging.critical('FAILING HARD')
            sys.exit()

        self.pins[pin.pin_designator] = pin

    def info(self) -> str:
        print(f'total pins: {len(self.pins.keys())}')

    def treeify(self, pin_dump: Dict[Optional[str], Dict[Optional[str], List[Pin]]]):
        tree = Tree()

        fpid = uuid.uuid4()
        tree.create_node('fpga', fpid)
        for bank, bcontents in pin_dump.items():
            bid = uuid.uuid4()
            tree.create_node('bank: ' + str(bank), bid, parent=fpid)
            for dqs, dcontents in bcontents.items():
                dqid = uuid.uuid4()
                tree.create_node('dqs: ' + str(dqs), dqid, parent=bid)
                if isinstance(dcontents, dict):
                    for gname, gpins in dcontents.items():
                        pid = uuid.uuid4()
                        tree.create_node(str(gname), pid, parent=dqid)
                        for gpin in gpins:
                            ppid = uuid.uuid4()
                            tree.create_node(str(gpin), ppid, parent=pid)
                else:
                    for pin in dcontents:
                        pid = uuid.uuid4()
                        tree.create_node(f'{str(pin)} {type(pin)}', pid, parent=dqid)
        tree.show()

    def dump_groups(self) -> Dict[str, Pin]:
        resd: Dict[str, List[Pin]] = {}
        bankset: Set[str] = set(p.bank for p in self.pins.values())
        for bank in bankset:
            resd[bank] = []

        for p in self.pins.values():
            resd[p.bank].append(p)
        return resd

    def dump_dqs(self, pins: List[Pin]) -> Dict[str, List[Pin]]:
        def unify(arg) -> str:
            if arg is None:
                return None

            intl: List[int] = []
            for c in arg:
                try:
                    intl.append(int(c))
                except ValueError:
                    pass

            return arg[0:3] + ''.join(str(i) for i in intl)

        resd: Dict[str, List[Pin]] = {}

        dqqset: Set[str] = set(unify(p.dqs) for p in pins)

        for dqs in dqqset:
            resd[dqs] = []

        for p in pins:
            resd[unify(p.dqs)].append(p)

        return resd

    def dump_pio(self, pins: List[Pin]) -> Tuple[bool, Dict[str, List[Pin]]]:
        resd: Dict[str, List[Pin]] = {}
        pioset: Set[str] = set(p.pio_num for p in pins)
        if len(pioset) < 2:
            return False, {}

        for pio in pioset:
            resd[pio] = []
        for p in pins:
            resd[p.pio_num].append(p)
        return True, resd
