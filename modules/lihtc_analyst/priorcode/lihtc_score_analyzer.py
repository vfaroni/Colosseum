            # If no app_type specified, analyze both
            for app_type in ['4%', '9%']:
                # Create subdirectory for each type
                type_dir = os.path.join(args.output_dir, app_type.replace('%', 'pct'))
                os.makedirs(type_dir, exist_ok=True)
                
                # Analyze score distribution
                analyzer.analyze_score_distribution(app_type=app_type, year=args.year, 
                                                  output_dir=type_dir)
                
                # Analyze category performance
                analyzer.analyze_category_performance(app_type=app_type, year=args.year,
                                                   output_dir=type_dir)
    
    print(f"Analysis complete. Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()