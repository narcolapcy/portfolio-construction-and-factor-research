# Required input schema

No licensed observations are included. Sheet and field names below document how the archived notebooks address their local inputs.

| Local input path expected from the notebook directory | Sheet | Structure |
| --- | --- | --- |
| `Data/Price_Data.xlsx` | `Weekly` | `Date`, then three benchmark series and 10 equity price series |
| `Data/Market_Value.xlsx` | `Weekly` | `Date`, equity market values, and `TOTAL` used in weight calculations |
| `HML/MV-PV.xlsx` | `PB` | Price-to-book values by equity; code uses reciprocal values to split groups |
| `SMB/MV.xlsx` | `MV` | A leading identifier/date column followed by equity market values |

The original price columns are `SPX.GI`, `DJI.GI`, `IXIC.GI`, `AAPL.O`, `MSFT.O`, `AMZN.O`, `JPM.N`, `V.N`, `JNJ.N`, `WMT.N`, `BAC.N`, `BRK_B.N`, `XOM.N`. These are field identifiers only; no price records are distributed.

The FAMA notebook also requests the FRED `DGS3MO` series through pandas-datareader. The archived code queries a broader date interval than the price sample. Any replication must align dates, frequencies and percent/decimal conventions correctly.

Keep authorized local input files untracked. The archive's expected path structure is a usage note, not permission to acquire or redistribute any vendor data.
