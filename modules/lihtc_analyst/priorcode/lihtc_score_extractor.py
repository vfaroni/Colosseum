                    # Look for numerator component
                    if 'numerator' in cell_text and not tie_breaker['components'].get('numerator'):
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)) and val > 0:
                                tie_breaker['components']['numerator'] = val
                                break
                    
                    # Look for denominator component
                    if 'denominator' in cell_text and not tie_breaker['components'].get('denominator'):
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)) and val > 0:
                                tie_breaker['components']['denominator'] = val
                                break
                    
                    # Look for specific subcomponents
                    if 'unit production benefit' in cell_text:
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)):
                                tie_breaker['components']['unitProductionBenefit'] = val
                                break
                    
                    if 'rent savings benefit' in cell_text:
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)):
                                tie_breaker['components']['rentSavingsBenefit'] = val
                                break
                    
                    if 'special needs population benefit' in cell_text:
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)):
                                tie_breaker['components']['specialNeedsBenefit'] = val
                                break
                    
                    if 'bond request' in cell_text:
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)) and val > 0:
                                tie_breaker['components']['bondRequest'] = val
                                break
                    
                    if 'state credits' in cell_text:
                        for c in range(col + 1, col + 5):
                            val = sheet.cell(row=row, column=c).value
                            if isinstance(val, (int, float)):
                                tie_breaker['components']['stateCredits'] = val
                                break
        else:
            # This might be a different format or an older application
            # Try to find any tie breaker related info
            for row in range(1, min(sheet.max_row, 100)):
                cell_a = sheet.cell(row=row, column=1).value
                
                if not cell_a:
                    continue
                
                cell_text = str(cell_a).lower()
                
                # Look for public benefit related terms
                if ('public benefit' in cell_text or 'bond allocation' in cell_text or 
                    'numerator' in cell_text or 'denominator' in cell_text):
                    
                    # Check columns to the right for values
                    for col in range(2, 8):
                        val = sheet.cell(row=row, column=col).value
                        if isinstance(val, (int, float)) and val > 0:
                            if 'numerator' in cell_text or 'public benefit' in cell_text:
                                tie_breaker['components']['numerator'] = val
                            elif 'denominator' in cell_text or 'bond allocation' in cell_text:
                                tie_breaker['components']['denominator'] = val
                            break
        
        # If we have the components but no score, calculate it
        if ('numerator' in tie_breaker['components'] and 
            'denominator' in tie_breaker['components'] and
            tie_breaker['score'] is None and
            tie_breaker['components']['denominator'] > 0):
            
            tie_breaker['score'] = (tie_breaker['components']['numerator'] / 
                                  tie_breaker['components']['denominator'])
        
        return tie_breaker


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Extract scoring data from LIHTC applications')
    parser.add_argument('--input_dir', required=True, help='Directory containing LIHTC Excel application files')
    parser.add_argument('--output_dir', required=True, help='Base directory for output JSON files')
    parser.add_argument('--parallel', action='store_true', help='Use parallel processing')
    parser.add_argument('--limit', type=int, help='Limit number of files to process (for testing)')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = LIHTCScoreExtractor(args.input_dir, args.output_dir, args.parallel)
    
    # Process files
    stats = extractor.process_all_files()
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total files found: {stats['total_files']}")
    print(f"Files processed: {stats['processed_files']}")
    print(f"Files skipped (already exist): {stats['skipped_files']}")
    print(f"Failed files: {stats['failed_files']}")
    print(f"9% applications: {stats['9pct_files']}")
    print(f"4% applications: {stats['4pct_files']}")


if __name__ == "__main__":
    main()