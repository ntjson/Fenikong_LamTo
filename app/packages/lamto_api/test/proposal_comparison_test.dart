import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';

// tests for ProposalComparison
void main() {
  final instance = ProposalComparisonBuilder();
  // TODO add properties to the builder and call build()

  group(ProposalComparison, () {
    // Direction of comparison: above, below, or equal.
    // String direction
    test('to test the property `direction`', () async {
      // TODO
    });

    // Difference percentage against the predicted price band.
    // int percentage
    test('to test the property `percentage`', () async {
      // TODO
    });

    // Formatted range string of the predicted price band.
    // String range
    test('to test the property `range`', () async {
      // TODO
    });

    // One-sentence Vietnamese reasoning explaining the band.
    // String reasoning
    test('to test the property `reasoning`', () async {
      // TODO
    });

    // Source of the prediction: predicted or fallback.
    // String source_
    test('to test the property `source_`', () async {
      // TODO
    });

  });
}
