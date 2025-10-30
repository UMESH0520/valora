from __future__ import annotations

from pyteal import *

# Box keys: bytes(product_id) => tuple(lowest_paise, display_paise)
# We store as ABI tuple to keep it compact.

ORACLE_ADDR = Bytes("oracle")  # set at deploy via global state


class PriceApp:
    def __init__(self) -> None:
        self.global_oracle = Bytes("oracle")  # bytes address

    def approval(self) -> Expr:
        product_id = Txn.application_args[1]
        price = Btoi(Txn.application_args[2])

        # Creation call has no args
        creation = Txn.application_id() == Int(0)
        method = Txn.application_args[0]

        is_creator = Txn.sender() == Global.creator_address()
        oracle_ok = Txn.sender() == App.globalGet(self.global_oracle)
        authorized = Or(is_creator, oracle_ok)

        @Subroutine(TealType.none)
        def write_lowest(pid, p):
            return Seq(
                (lkey := ScratchVar()).store(Concat(Bytes("l:"), pid)),
                Pop(BoxCreate(lkey.load(), Int(8))),
                BoxPut(lkey.load(), Itob(p)),
            )

        @Subroutine(TealType.none)
        def write_display(pid, p):
            return Seq(
                (dkey := ScratchVar()).store(Concat(Bytes("d:"), pid)),
                Pop(BoxCreate(dkey.load(), Int(8))),
                BoxPut(dkey.load(), Itob(p)),
            )

        # If creation, just approve
        router = If(creation).Then(Approve()).Else(Cond(
            [
                And(method == Bytes("init"), Txn.application_args.length() == Int(2), Txn.sender() == Global.creator_address()),
                Seq(
                    App.globalPut(self.global_oracle, Txn.application_args[1]),
                    Approve(),
                ),
            ],
            [
                And(method == Bytes("update_lowest"), Txn.application_args.length() == Int(3)),
                Seq(Assert(authorized), write_lowest(product_id, price), Approve()),
            ],
            [
                And(method == Bytes("update_display"), Txn.application_args.length() == Int(3)),
                Seq(Assert(authorized), write_display(product_id, price), Approve()),
            ],
        ))

        program = Seq(router, Reject())
        return program

    def clear(self) -> Expr:
        return Approve()


if __name__ == "__main__":
    # quick compile helper
    app = PriceApp()
    print(compileTeal(app.approval(), mode=Mode.Application, version=8))
