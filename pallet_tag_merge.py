import csv
import math
import decimal


class Pallet:
    def __init__(self):
        self.stackdata = {}
        self.palletdata = {}

    def set_pallet_data(self, palletn, palletmax, stacksheets, last_pallet=None):

        if last_pallet:
            self.palletdata["palletstart"] = (((palletn - 1) * palletmax)) + 1
            self.palletdata["palletend"] = ((palletn - 1) * palletmax) + last_pallet
            self.palletdata["palletqty"] = (self.palletdata["palletend"] -
                                            self.palletdata["palletstart"]) + 1

            self.palletdata["palletstackcnt"] = math.ceil(decimal.Decimal(self.palletdata["palletqty"]) /
                                                          decimal.Decimal(stacksheets))


        else:
            self.palletdata["palletstart"] = (((palletn - 1) * palletmax)) + 1
            self.palletdata["palletend"] = palletn * palletmax
            self.palletdata["palletqty"] = (self.palletdata["palletend"] -
                                            self.palletdata["palletstart"]) + 1

            self.palletdata["palletstackcnt"] = int((self.palletdata["palletqty"] /
                                                     stacksheets) / 2)

    def _is_last_stack(self, stacksheets, stackn, jobtotal):
        leftstart = ((stackn - 1) * stacksheets) + self.palletdata["palletstart"]
        leftend = (leftstart - 1) + stacksheets
        return (leftend + int(self.palletdata["palletqty"] / 2) > jobtotal)

    def set_stack_data(self, palletn, stackn, stacksheets, palletmax):
        self.stackdata["leftstart"] = ((stackn - 1) * stacksheets) + self.palletdata["palletstart"]
        self.stackdata["leftend"] = (self.stackdata["leftstart"] - 1) + stacksheets
        self.stackdata["rightstart"] = self.stackdata["leftstart"] + int(palletmax / 2)
        self.stackdata["rightend"] = self.stackdata["leftend"] + int(palletmax / 2)

    def set_last_pallet_stack_data(self, palletn, stackn, stacksheets, palletmax, jobtotal):
        # if last stack on last pallet
        if self._is_last_stack(stacksheets, stackn, jobtotal):
            # print('last stack')
            self._last_stack_qty = jobtotal - (int(self.palletdata["palletqty"] / 2) + self.stackdata["leftend"])
            self.stackdata["leftstart"] = ((stackn - 1) * stacksheets) + self.palletdata["palletstart"]
            self.stackdata["leftend"] = (self.stackdata["leftstart"] - 1) + self._last_stack_qty
            self.stackdata["rightstart"] = (jobtotal - self._last_stack_qty + 1)
            self.stackdata["rightend"] = jobtotal
        # if not last stack on last pallet
        else:
            self.stackdata["leftstart"] = ((stackn - 1) * stacksheets) + self.palletdata["palletstart"]
            self.stackdata["leftend"] = (self.stackdata["leftstart"] - 1) + stacksheets
            self.stackdata["rightstart"] = self.stackdata["leftstart"] + int(self.palletdata["palletqty"] / 2)
            self.stackdata["rightend"] = self.stackdata["rightstart"] + (stacksheets - 1)


def process_tags(ver, pallet_max, stack_sheets, total_rec):

    total_pallets = math.ceil(total_rec / pallet_max)
    last_pallet = (total_rec % pallet_max)
    header = ["file", "stack", "lstart", "lend", "rstart", "rend", "stackqty"]

    with open("{} tags.tab".format(ver), "w+", newline='') as csvfile:
        f = csv.writer(csvfile, delimiter='\t', dialect='excel', quoting=csv.QUOTE_ALL)
        f.writerow(header)

        # if the last pallet is not a full pallet (job total % pallet total != 0)
        if last_pallet:
            # Up to last pallet
            for palletn in range(1, total_pallets):
                pallet = Pallet()
                pallet.set_pallet_data(palletn, pallet_max, stack_sheets)

                for stack in range(1, (pallet.palletdata["palletstackcnt"] + 1)):
                    pallet.set_stack_data(palletn, stack, stack_sheets, pallet_max)
                    # print("Pallet {0}: Stack {1} ".format(str(palletn), str(stack)),
                    #       pallet.stackdata)
                    f.writerow(["{0}_P{1}.tab".format(ver, str(palletn)),
                                stack, pallet.stackdata["leftstart"], pallet.stackdata["leftend"],
                                pallet.stackdata["rightstart"], pallet.stackdata["rightend"],
                                str((pallet.stackdata["leftend"] + 1) - pallet.stackdata["leftstart"])
                                ])

            # last Pallet
            pallet = Pallet()
            pallet.set_pallet_data(total_pallets, pallet_max, stack_sheets, last_pallet)

            try:
                palletn
            except NameError:
                palletn = 1

            for stack in range(1, int((pallet.palletdata["palletstackcnt"] + 1) / 2) + 1):
                pallet.set_last_pallet_stack_data(palletn, stack, stack_sheets, pallet_max, total_rec)

                f.writerow(["{0}_P{1}.tab".format(ver, total_pallets),
                            stack, pallet.stackdata["leftstart"], pallet.stackdata["leftend"],
                            pallet.stackdata["rightstart"], pallet.stackdata["rightend"],
                            str((pallet.stackdata["leftend"] + 1) - pallet.stackdata["leftstart"])
                            ])

        # if the job breaks evenly at a full pallet
        else:
            for palletn in range(1, (total_pallets + 1)):
                pallet = Pallet()
                pallet.set_pallet_data(palletn, pallet_max, stack_sheets)

                for stack in range(1, (pallet.palletdata["palletstackcnt"] + 1)):
                    pallet.set_stack_data(palletn, stack, stack_sheets, pallet_max)
                    # print("Pallet {0}: Stack {1} ".format(str(palletn), str(stack)),
                    #       pallet.stackdata)
                    f.writerow(["{0}_P{1}.tab".format(ver, str(palletn)),
                                stack, pallet.stackdata["leftstart"], pallet.stackdata["leftend"],
                                pallet.stackdata["rightstart"], pallet.stackdata["rightend"],
                                str((pallet.stackdata["leftend"] + 1) - pallet.stackdata["leftstart"])
                                ])


def main():
    ver = "C04"
    pallet_max = 90000
    stack_sheets = 5000
    total_rec = 975596

    # ver = input('Version Code: ')
    # pallet_max = input('Max records per pallet: ')
    # stack_sheets = input('Max sheets per stack: ')
    # total_rec = int(input('Total job records: '))

    if ver and pallet_max and stack_sheets and total_rec:
        process_tags(ver, pallet_max, stack_sheets, total_rec)


if __name__ == '__main__':
    main()
