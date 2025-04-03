with open('einkpalatte7-ditheredImage.bin', 'rb') as f1, open('einkpalatte7-ditheredImage-js.bin', 'rb') as f2:
    content1 = f1.read()
    content2 = f2.read()
    
    if len(content1) != len(content2):
        print(f"Files have different sizes: {len(content1)} vs {len(content2)} bytes")
    else:
        print(f"Files have same size: {len(content1)} bytes")
    
    # Dictionary to store unique differences
    diff_patterns = {}  # (byte1, byte2) -> [positions]
    
    for i, (b1, b2) in enumerate(zip(content1, content2)):
        if b1 != b2:
            key = (b1, b2)
            if key not in diff_patterns:
                diff_patterns[key] = []
            diff_patterns[key].append(i)
    
    if not diff_patterns:
        print("Files are identical")
    else:
        # Create a list of tuples sorted by occurrence count (descending)
        sorted_patterns = []
        for (b1, b2), positions in diff_patterns.items():
            sorted_patterns.append(((b1, b2), positions))
        
        # Sort by the length of the positions list (number of occurrences)
        sorted_patterns.sort(key=lambda x: len(x[1]), reverse=True)
        
        print("\nUnique differences found:")
        for (b1, b2), positions in sorted_patterns[:10]:
            print(f"\nPattern: Correct: {hex(b1)} -> Our version: {hex(b2)}")
            print(f"Occurs at {len(positions)} positions:")
            #print(f"First few positions: {positions[:5]}")
            #if len(positions) > 5:
                #print(f"... and {len(positions) - 5} more positions")