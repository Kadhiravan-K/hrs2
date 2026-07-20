# Report Guide

## Overview

The system generates patient visit reports in PDF format. Reports are created from the completed visit draft and include patient, doctor, symptoms, sensor values, and summary information.

## Report generation flow

1. The user completes registration and sensor collection.
2. The visit draft is prepared.
3. The report preview is shown.
4. A PDF report is generated.

## Output location

Generated reports are stored in the `reports/` folder.

## Notes

- Report generation depends on the completed visit draft.
- The report content is built from the collected patient and visit information.
- A preview screen is shown before the final PDF is created.
