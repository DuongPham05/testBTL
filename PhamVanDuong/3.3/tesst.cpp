#include <GL/glut.h>
void draw(void) {
	glClear(GL_COLOR_BUFFER_BIT); /*xóa mọi pixel */

	glColor3f(1.0, 0.0, 0.0); /*thiết lập màu vẽ */
	glBegin(GL_LINES); /*gọi hàm vẽ đoạn thẳng */
	glVertex2f(0.0, 0.0); /*khai báo điểm đầu đoạn thẳng */
	glVertex2f(0.5, 0.0); /*khai báo điểm cuối đoạn thẳng */
	glEnd(); /*kết thúc vẽ */
	glFlush(); /*thực thi lệnh vẽ */
}
int main() {

	glutCreateWindow("hello"); /*	tạo cửa sổ đồ họa đặt tên là ‘hello’ */
	glClearColor(0.0, 0.0, 0.0, 0.0); /*nền màu đen */

	glutDisplayFunc(draw); /*gọi hàm vẽ ở trên */

	glutMainLoop(); /*bắt đầu chu trình vòng lặp vẽ, giúp cửa sổ vẽ luôn hiển thị hình ảnh cho đến khi người dùng đóng cửa sổ*/
	return 0;
}
