class NoDesignationError(Exception):
    "No Designation found in the request"
    pass

class NoWFHSetupAvailabilityError(Exception):
    "No WFH Setup Availability found in the request"
    pass

class NoResourceAllocationError(Exception):
    "No Resource Allocation found in the request"
    pass

class NoMentalFatigueScoreError(Exception):
    "No Mental Fatigue Score found in the request"
    pass

class NoCSVFileError(Exception):
    "No CSV file found in the request"
    pass