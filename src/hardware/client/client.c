/******************************************************************************
*
* Copyright (C) 2009 - 2014 Xilinx, Inc.  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* Use of the Software is limited solely to applications:
* (a) running on a Xilinx device, or
* (b) that interact with a Xilinx device through a bus or interconnect.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* Except as contained in this notice, the name of the Xilinx shall not be used
* in advertising or otherwise to promote the sale, use or other dealings in
* this Software without prior written authorization from Xilinx.
*
******************************************************************************/

#include <stdio.h>
#include <string.h>

#include "lwip/err.h"
#include "lwip/tcp.h"
#if defined (__arm__) || defined (__aarch64__)
#include "xil_printf.h"
#endif
static int state = 0;
volatile unsigned int * result = (unsigned int *)0x40000000;
volatile unsigned int * ratio = (unsigned int *)0x40010000;
int transfer_data() {
	return state;
}

void print_app_header()
{
	xil_printf("\n\r\n\r-----lwIP TCP echo server ------\n\r");
	xil_printf("TCP packets sent to port 6001 will be echoed back\n\r");
}

err_t sent_callback(void *arg, struct tcp_pcb *tpcb,
        u16_t len)
{
	xil_printf("message sent, number of bytes sent: %d\n\r", len);
	/* set the receive callback for this connection */
	state = 1;
	tcp_close(tpcb);
	return ERR_OK;
}

err_t recv_callback(void *arg, struct tcp_pcb *tpcb,
                               struct pbuf *p, err_t err)
{
	char buf[1024] = {};
	xil_printf("message recieved!!!\n\r");
	/* do not read the packet if we are not in ESTABLISHED state */
	if (!p) {
		tcp_close(tpcb);
		tcp_recv(tpcb, NULL);
		return ERR_OK;
	}

	/* indicate that the packet has been received */
	tcp_recved(tpcb, p->len);
	state = 1;
	strncpy(buf, p->payload, p->len);
	xil_printf("set message received, length: %d, msg: %s\n\r", p->len, buf);

	/* free the received pbuf */
	pbuf_free(p);
	tcp_close(tpcb);
	return ERR_OK;
}

err_t connect_callback(void *arg, struct tcp_pcb *tpcb, err_t err){
	char buf[1024]= {};
//	xil_printf("query connection established...\n\r");
//	tcp_recv(tpcb, recv_callback);
	snprintf(buf, 10, "%4d:%4d", *ratio, *result);
	xil_printf("sending msg:%s\n\r", buf);
	fflush(stdout);
	err = tcp_write(tpcb, (void *)buf, 10, 1);
	tcp_output(tpcb);
	tcp_sent(tpcb, sent_callback);
	return ERR_OK;
}

//void error_callback(void *arg, err_t err){
//	xil_printf("error code: %d\n\r",err);
//}

int start_application()
{
	struct tcp_pcb *pcb;
	err_t err;
	unsigned port = 7;
	state = 0;
	struct ip_addr ipaddr;
	IP4_ADDR(&ipaddr,192,168, 1, 11);
	/* create new TCP PCB structure */
	pcb = tcp_new();
	if (!pcb) {
		xil_printf("Error creating PCB. Out of Memory\n\r");
		return -1;
	}

	tcp_arg(pcb, NULL);

//	xil_printf("connecting to host...\n\r");
	err = tcp_connect(pcb, &ipaddr, port, connect_callback);
	if (err != ERR_OK) {
		xil_printf("Unable to connect to port %d: err = %d\n\r", port, err);
		return -2;
	}
//	tcp_err(pcb, error_callback);
//	xil_printf("TCP echo client started\n\r");
	return 0;
}
