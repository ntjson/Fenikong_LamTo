---
status: accepted
---

# Open documents inside the Resident app, and keep the explorer external

A document the Resident app has fetched — a transfer proof on a spend, the PDF
or image on a bill — opens in a viewer screen inside the app. Previously the
app wrote the bytes to a temporary file and handed that file to the operating
system share sheet, so reading a payment record meant leaving LamTo for
whatever app the resident picked out of a list. A product whose claim is that a
resident can check a spend for themselves cannot make the last step of checking
it an excursion.

This is not a reversal of ADR 0004. That decision rejected a WebView for the
Evidence explorer, and it still stands: **the explorer opens in the external
browser**, because seeing the real URL, and being able to share it or reopen it
on a PC, is part of what makes the page proof. The distinction is between a
*page whose address is evidence* and a *document whose bytes are evidence*. A
URL the resident cannot see is a weaker claim; a document the resident cannot
read without leaving is a worse one.

The share action survives inside the viewer for 0004's own reasoning: a
resident is entitled to take a copy of the evidence out of LamTo — to their own
storage, to an inspector, to print. Reading in-app is the default, not a fence.

## Considered options

Keeping the share sheet as the only path was rejected on the grounds above. A
WebView pointed at the document URL was rejected because the app already holds
the bytes it authenticated for, and re-fetching them in a component with its
own cookie and cache behaviour adds a second, weaker trust path to the same
bytes.

## Consequences

The renderer is chosen from the stored content type the API ships, and the
document's leading bytes override that when the two disagree, so a mislabelled
record renders instead of blanking. The filename extension is never consulted:
it is upload data, and letting an uploader's chosen extension select a parser
would let the upload decide how it is read.

Fetch failures and render failures stay distinct. A network, authentication or
permission failure appears on the document row with a retry and no viewer is
pushed — the viewer opens only once the bytes are in hand, so it can never show
a blank screen. A file LamTo cannot draw shows a plain sentence inside the
viewer with the share action still offered: a document the app cannot render is
still a document the resident is entitled to have.

Sharing hands the bytes over as data rather than as a file LamTo has written,
so the app keeps no copy of a resident's evidence on disk; the share
implementation stages its own temporary file and the system reclaims it.

PDF rendering is PDFium via `pdfrx`, which `flutter test` cannot load. Widget
tests therefore assert renderer selection and failure copy, and
`integration_test/document_viewer_test.dart` asserts on a device that pages
actually render.
