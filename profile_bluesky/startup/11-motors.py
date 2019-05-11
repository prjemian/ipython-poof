print(__file__)

"""motors, stages, positioners, ..."""

# m1 = MyEpicsMotorWithDial('xxx:m1', name='m1')
m1 = EpicsMotor('xxx:m1', name='m1', labels=["motor",])
m2 = EpicsMotor('xxx:m2', name='m2', labels=["motor",])
m3 = EpicsMotor('xxx:m3', name='m3', labels=["motor",])
m4 = EpicsMotor('xxx:m4', name='m4', labels=["motor",])
m5 = EpicsMotor('xxx:m5', name='m5', labels=["motor",])
m6 = EpicsMotor('xxx:m6', name='m6', labels=["motor",])
m7 = EpicsMotor('xxx:m7', name='m7', labels=["motor",])
m8 = EpicsMotor('xxx:m8', name='m8', labels=["motor",])
