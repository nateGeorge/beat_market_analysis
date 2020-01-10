# beat_market_analysis
This was an attempt to reproduce the results from this paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3184501

The conclusion is that the paper is bogus, and the author has either purposefully or accidentally overfit a strategy to past data.  The idea is to buy the smallest market cap stocks from an index like the SP600.  The results of the paper of course show incredible results, and claim it's easy to beat the market.  However, there were additional parameters used to filter the stocks, so it's not nearly as simple as taking the smallest market cap stocks.  The additional filters were not specified, leading me to believe the author knowingly created a paper with sensational results yet faulty and dishonest analysis.


I originally discovered this analysis from this video: https://www.youtube.com/watch?v=7gbcEkiozCc&feature=youtu.be
which has a rebalance period of 12 months instead of 24 like in the paper (at 5:48).


# data details
definitions of important columns:

Effective From Date (from) -- the date the company was added to the index
Effective Thru Date (thru) -- the date the company was deleted from the index

spii -- S&P industry index code
spmi -- S&P major index code

GVKEY is a unique
permanent number assigned by Compustat, that can be
used to identify a Compustat record in different updates if
name or other identifying information changes. GVKEY is
the primary key in the CRSP/Compustat Merged Database.
Data are sorted and organized by this field

IID -- Compustat’s permanent issue identifier. An
identifying relationship exists between IID
and GVKEY. Both must be accessed as a pair
to properly identify a Compustat security.
One GVKEY can have multiple IIDs.
Because Compustat company data ranges can
extend earlier than security ranges, there may
be some time periods with no identified IID
for a GVKEY. In these cases, CRSP assigns a
dummy IID ending in “X” as a placeholder
in the link. This range may or may not be
associated with a CRSP PERMNO, but there
is no Compustat security data found during
the range when no IID is assigned.

gvkeyx – Compustat index key

co_conm -- company name

co_tic -- company ticker

cik -- CIK number

sic -- SIC code

naics -- North American Industry Classification Code

http://www.crsp.com/files/ccm_data_guide_0.pdf
https://datateamoftheeur.files.wordpress.com/2016/07/index_constituents-compustat_north_america.pdf
