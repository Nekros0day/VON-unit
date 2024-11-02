function note = assemblerv3(infile)
MemData = zeros(1,32768,'uint8');

AdrIndex = zeros(1,32768,'uint16');

MemoryChip = fopen('MemChip.bin','w');
opts = detectImportOptions(infile,'TextType','string');
opts.DataLines = [1,Inf]
opts.Delimiter = {' '}
FixFile = readmatrix(infile, opts);
SpecialIns = ["LDA", "LDB", "LDC", "LDD", "LDX", "LDY", "ADD", "SUB", "XOR", "STA", "JMP", "JAZ", "JXZ", "JYZ", "JMS"];
Instructions = ["LDA", "LDB", "LDC", "LDD", "LDX", "LDY", "LPR", "ADD", "SUB", "XOR", "OUT", "ITA", "STA", "JMP", "JAZ", "JXZ", "JYZ", "JMS", "RFS", "XIC", "YIC", "XDC", "YDC", "DIQ", "HLT", "ICR", "CMP", "LDI", "NA", "NA", "NA", "NA", "NA",];
[Rows,Cols] = size(FixFile);
File = strings([Rows*2,Cols])
padI = 0;
PosIndex = 0;
for i = 1:Rows
    if ~isempty(find(SpecialIns == FixFile(i,1), 1))
        File(i+padI, 1) = "LPR";
        File(i+padI, 2) = FixFile(i, 2)
        File(i+padI, 3) = FixFile(i, 3)
        padI = padI+1;
        File(i+padI, 1) = FixFile(i, 1)      
    end
    if isempty(find(SpecialIns == FixFile(i,1), 1))
        for k = 1:Cols
        File(i+padI,k) = FixFile(i,k)
        end
    end
end
[Rows,Cols] = size(File);
adr = int16(0)
for i = 1:Rows 
    if Cols == 3
    if ~isempty(str2num(strip(File(i,3),'left','@')))
        revAdr = adr;
        adr = str2num(strip(File(i,3),'left','@'))
    end
    if strip(File(i,3),'left','@') == "return"
        adr = revAdr;
    end
    end
    for j = 1:2
        if j == 2
            if contains(File(i,j), "@")
                n = str2num(strip(File(i,2),'left','@'));
                    if File(i,j-1) == "LPR"
                            adr = adr+1;
                            MemData(adr) = 0;
                            adr = adr+1;
                            MemData(adr) = 0;
                    end
                    if ~(File(i,j-1) == "LPR")
                        adr = adr+1;
                        MemData(adr) = n;
                    end
            end
            if ~contains(File(i,j), "@")
                n = str2num(File(i,j));
                if ~isempty(n)
                    if File(i,j-1) == "LPR"
                            adr = adr+1;
                            MemData(adr) = 0;
                            adr = adr+1;
                            MemData(adr) = 0;
                    end
                    if (File(i,j-1) == "LDI") | (File(i,j-1) == "ICR")
                        adr = adr+1;
                        MemData(adr) = str2num(File(i,j));
                    end

                end
            end
        end
        if j == 1
            if ~isempty(find(Instructions == File(i,j), 1))
            s = find(Instructions == File(i,j), 1)
            adr = adr+1;
            if ~isempty(s)
            MemData(adr) = s - 1;
            AdrIndexLPR(i) = adr -1
            if ~(s == 7)
            PosIndex = PosIndex + 1
            AdrIndex(PosIndex) = adr -1
            end
            end
            end
            
            if (~isempty(double(char(File(i,j)))) |  ~isempty(str2num(strip(File(i,j),'left','#')))) & isempty(find(Instructions == File(i,j), 1))
                adr = adr+1
                if contains(File(i,j), "#")
                   MemData(adr) = str2num(strip(File(i,j),'left','#'));
                   AdrIndexLPR(i) = adr -1
                   PosIndex = PosIndex + 1
                   AdrIndex(PosIndex) = adr -1
                end
                if ~contains(File(i,j), "#")
                   MemData(adr) = double(char(File(i,j)));
                   AdrIndexLPR(i) = adr -1
                   PosIndex = PosIndex + 1
                   AdrIndex(PosIndex) = adr -1
                end
            end
        end
    end
end
for i = 1:Rows 
    if File(i,1) == "LPR"
        
        if contains(File(i,2), "@")
        N = str2num(strip(File(i,2),'left','@'));
        adr = AdrIndexLPR(i)+1
        end
        
        if ~contains(File(i,2), "@")
        N = AdrIndex(str2num(File(i,2)))
        adr = AdrIndexLPR(i)+1
        end
        
        b = dec2bin(N, 16);
        b1 = bin2dec(b(1:8));
        b2 = bin2dec(b(9:16));
        adr = adr+1;
        MemData(adr) = b2;
        adr = adr+1;
        MemData(adr) = b1;

    end
end

disp("DONE!")
fwrite(MemoryChip,MemData);
fclose(MemoryChip);