`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2014/05/23 15:48:40
// Design Name: 
// Module Name: vga
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

// This module assumes a QVGA 320 x 240 image will be displayed in the middle
// of a 640 x 480 VGA screen.
// This module integrates the image recognition algorithm

module aspect_ratio(
input clk25,
output [9:0] ratio,
output [16:0] frame_addr,
input [15:0] frame_pixel
    );
    //Timing constants
      parameter hRez   = 640;
      parameter hStartSync   = 640+16;
      parameter hEndSync     = 640+16+96;
      parameter hMaxCount    = 800;
    
      parameter vRez         = 480;
      parameter vStartSync   = 480+10;
      parameter vEndSync     = 480+10+2;
      parameter vMaxCount    = 480+10+2+33;
    
    parameter hsync_active   =0;
    parameter vsync_active  = 0;
    
    reg[9:0] hCounter;
    reg[9:0] vCounter;    
    reg[16:0] address;  
    reg blank;
    reg[9:0] hmax_reg;
    reg[9:0] hmin_reg;
    reg[9:0] vmax_reg;
    reg[9:0] vmin_reg;
    reg[9:0] hdiff_reg;
    reg[9:0] vdiff_reg;
    reg[9:0] ratio_reg;
	reg[3:0] vga_red;
	reg[3:0] vga_green;
	reg[3:0] vga_blue;
	reg vga_hsync;
	reg vga_vsync;
    reg hflag;
    reg vflag;
   initial   hCounter = 10'b0;
   initial   vCounter = 10'b0;
   initial   hmax_reg = 10'b0;
   initial   hmin_reg = 10'b1111111111;
   initial   vmax_reg = 10'b0;
   initial   vmin_reg = 10'b0;
   initial   hdiff_reg = 10'b0;
   initial   vdiff_reg = 10'b0;  
   initial   address = 17'b0;   
   initial   blank = 1'b1;    
   initial   fCounter = 32'b0;
   initial   pout_reg = 7'b0;
   initial   hflag = 1'b0;
   initial   vflag = 1'b0;
   
   assign frame_addr = address;
//   assign HCnt = hCounter;
//   assign VCnt = vCounter;
   assign ratio = ratio_reg;
//   assign hdiff = hdiff_reg;
//   assign vdiff = vdiff_reg;
   
   
   always@(posedge clk25)begin
            if( hCounter == hMaxCount-1 )begin
   				hCounter <=  10'b0;
   				hflag <= 1'b0;
   				if (vCounter == vMaxCount-1 )
   				begin
   					vCounter <=  10'b0;
   					hdiff_reg <= hmax_reg - hmin_reg;
                    vdiff_reg <= vmax_reg - vmin_reg;
                    if (hdiff_reg == 0)
                    begin
                        ratio_reg <= 10'b0;
                    end
                    else
                    begin
                        ratio_reg <= (vdiff_reg * 100) / hdiff_reg;
                    end
                    hmin_reg <= 10'b1111111111;
                    hmax_reg <= 10'b0;
                    vmin_reg <= 10'b0;
                    vmax_reg <= 10'b0;
                    vflag <= 1'b0;
                end
   				else
   					vCounter <= vCounter+1;
   				end
   			else
   				hCounter <= hCounter+1;
   			if (blank == 0) 
   			begin
   				vga_red   <= frame_pixel[11:8];
   				vga_green <= frame_pixel[7:4];
   				vga_blue  <= frame_pixel[3:0];
   				if (vga_red >= threshold)
                begin
                    pCounter <= pCounter + 1;
                end
                if (vga_red >= threshold_aspect)
                begin
                    if (vmin_reg == 0)
                    begin
                       vmin_reg <= vCounter; 
                    end
                    if (vCounter > vmax_reg)
                    begin
                        vmax_reg <= vCounter;
                    end
                    if (hCounter < hmin_reg)
                    begin
                        hmin_reg <= hCounter;
                    end
                    if (hCounter > hmax_reg)
                    begin
                        hmax_reg <= hCounter;
                    end
                end
   		    end
   			else begin
   				vga_red   <= 4'b0;
   				vga_green <= 4'b0;
   				vga_blue  <= 4'b0;
   			     end;

                        // A 320 by 240 image is placed in the middle of a
                        //  640 by 480 screen
   			if(  vCounter  >= 360 || vCounter  < 120) begin
   				address <= 17'b0; 
   				blank <= 1;
   				end
   			else begin
   				if ( hCounter  < 480 && hCounter  >= 160) begin
   					blank <= 0;
   					address <= address+1;
   					end
   				else
   					blank <= 1;
   				end;
   	
   			// Are we in the hSync pulse? (one has been added to include frame_buffer_latency)
   			if( hCounter > hStartSync && hCounter <= hEndSync)
   				vga_hsync <= hsync_active;
   			else
   				vga_hsync <= ~ hsync_active;
   			
   
   			// Are we in the vSync pulse?
   			if( vCounter >= vStartSync && vCounter < vEndSync )
   				vga_vsync <= vsync_active;
   			else
   				vga_vsync <= ~ vsync_active;
   end 
endmodule
